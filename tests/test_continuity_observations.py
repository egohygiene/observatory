"""Offline metadata, privacy and compatible health-view controls."""
from contextlib import redirect_stderr
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from observatory.continuity import build_continuity_view, validate_view, OWNER_PIN
from observatory import public_reviews as shared
from observatory.health_cli import main
from test_health import build_fixture_snapshot, CATALOG, CATALOG_URL, CATALOG_COMMIT

FIXTURES = ROOT / "fixtures/continuity"
AS_OF = "2026-11-14T04:00:00Z"


class ContinuityObservationTests(unittest.TestCase):
    def setUp(self):
        self.wrappers = json.loads((FIXTURES / "observations.json").read_text())
        self.targets = json.loads((FIXTURES / "targets.json").read_text())

    def build(self, wrappers=None, targets=None, as_of=AS_OF):
        return build_continuity_view(self.wrappers if wrappers is None else wrappers,
            repositories=self.targets if targets is None else targets, as_of=as_of)

    def test_synthetic_state_coverage_schema_and_exact_expected_output(self):
        model = self.build()
        self.assertEqual(model, json.loads((FIXTURES / "expected.json").read_text()))
        self.assertEqual({row["posture"] for row in model["repositories"]},
            {"unverifiable", "valid", "absent", "invalid", "unsupported", "exempt", "stale-declared"})
        schema = json.loads((ROOT / "schemas/fleet-continuity.v1.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(model)
        self.assertEqual(validate_view(model), model)

    def test_private_and_unlisted_inputs_cannot_change_any_public_byte(self):
        expected = self.build()
        protected = {"visibility": "private", "repository": "egohygiene/synthetic-private-canary", "evidence": {"malformed": ["private"]}}
        public_unlisted = {**protected, "visibility": "public"}
        self.assertEqual(expected, self.build(self.wrappers + [protected, public_unlisted]))
        self.assertEqual(expected, self.build(targets=self.targets + [{"repository": protected["repository"], "represented_commit": "invalid-private"}]))
        nested = deepcopy(self.wrappers[0]); nested["evidence"]["source_url"] = "https://github.com/egohygiene/synthetic-private-canary/blob/hidden/file"
        self.assertEqual(self.build(self.wrappers[1:]), self.build(self.wrappers[1:] + [nested]))
        self.assertNotIn("synthetic-private-canary", json.dumps(expected))

    def test_order_is_deterministic_and_source_metadata_is_unchanged(self):
        original = deepcopy(self.wrappers)
        self.assertEqual(self.build(), self.build(list(reversed(self.wrappers)), list(reversed(self.targets))))
        self.assertEqual(original, self.wrappers)

    def test_missing_access_differs_from_observed_absence(self):
        rows = {r["repository"]["full_name"]: r for r in self.build()["repositories"]}
        self.assertEqual(rows["egohygiene/aether"]["collection"], "unavailable")
        self.assertEqual(rows["egohygiene/aether"]["posture"], "unverifiable")
        self.assertEqual(rows["egohygiene/mantle"]["posture"], "absent")

    def test_declaration_observation_git_and_live_freshness_remain_independent(self):
        row = next(r for r in self.build(as_of="2026-11-16T04:00:00Z")["repositories"] if r["repository"]["full_name"] == "egohygiene/observatory")
        self.assertEqual(row["posture"], "valid")
        self.assertEqual(row["observation_freshness"], "stale")
        self.assertEqual(row["latest"]["git"]["status"], "unverified")
        self.assertEqual(row["latest"]["live"]["status"], "unverified")

    def test_other_revision_cannot_establish_selected_revision_status(self):
        wrappers = deepcopy(self.wrappers)
        wrappers[0]["evidence"]["represented_commit"] = "c" * 40
        row = next(r for r in self.build(wrappers)["repositories"] if r["repository"]["full_name"] == "egohygiene/observatory")
        self.assertEqual(row["collection"], "other-revision-only")
        self.assertIsNone(row["latest"])

    def test_provisional_and_duplicate_pointer_boundaries(self):
        wrappers = deepcopy(self.wrappers)
        wrappers[0]["evidence"]["declared"]["status"] = "provisional"
        self.assertIn("provisional", {r["posture"] for r in self.build(wrappers)["repositories"]})
        wrappers[0]["evidence"]["pointer"]["managed_block_count"] = 2
        row = next(r for r in self.build(wrappers)["repositories"] if r["repository"]["full_name"] == "egohygiene/observatory")
        self.assertEqual(row["posture"], "invalid")

    def test_unknown_body_fields_and_bad_counts_fail_without_input_echo(self):
        for mutation in (lambda d:d.update(body="synthetic-private-canary"),
                         lambda d:d["structure"].update(error_count=True),
                         lambda d:d["structure"].update(error_count=1),
                         lambda d:d["pointer"].update(managed_block_count=True),
                         lambda d:d["live"].update(status="verified")):
            wrappers = deepcopy(self.wrappers); mutation(wrappers[0]["evidence"])
            with self.assertRaises(ValueError) as caught:
                self.build(wrappers)
            self.assertNotIn("synthetic-private-canary", str(caught.exception))

    def test_conflicting_same_revision_timestamp_is_rejected_but_duplicates_deduplicate(self):
        self.assertEqual(self.build(), self.build(self.wrappers + [deepcopy(self.wrappers[0])]))
        conflicting = deepcopy(self.wrappers[0]); conflicting["evidence"]["structure"]["warning_count"] = 1
        with self.assertRaises(ValueError): self.build(self.wrappers + [conflicting])

    def test_forged_output_and_pins_cannot_be_resealed_into_a_valid_view(self):
        model = self.build()
        model["repositories"][0]["posture"] = "valid"
        model = shared.seal({k:v for k,v in model.items() if k != "digest"})
        with self.assertRaises(ValueError): validate_view(model)
        model = self.build(); model["owner_contract"]["lifecycle"] = "stable"
        with self.assertRaises(ValueError): validate_view(model)

    def test_health_default_bytes_unchanged_and_selected_cli_view_is_bound(self):
        baseline = build_fixture_snapshot()
        self.assertNotIn("continuity", baseline)
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            targets = destination / "targets.json"; evidence = destination / "metadata.json"
            targets.write_text(json.dumps([self.targets[0]])); evidence.write_text(json.dumps([self.wrappers[0]]))
            args = ["build", "--catalog", str(CATALOG), "--catalog-url", CATALOG_URL, "--catalog-commit", CATALOG_COMMIT,
                    "--as-of", AS_OF, "--output", str(destination / "output"), "--continuity-targets", str(targets), "--continuity-evidence", str(evidence)]
            self.assertEqual(main(args), 0)
            output = json.loads((destination / "output/organization-health.json").read_text())
            self.assertEqual(len(output["continuity"]["repositories"]), 1)
            resource = json.loads((ROOT / "schemas/fleet-continuity.v1.schema.json").read_text())
            registry = Registry().with_resource(resource["$id"], Resource.from_contents(resource))
            Draft202012Validator(json.loads((ROOT / "schemas/organization-health.v1.schema.json").read_text()), registry=registry).validate(output)
            args.remove("--continuity-targets"); args.remove(str(targets))
            stderr = io.StringIO()
            with redirect_stderr(stderr): self.assertEqual(main(args), 2)
            self.assertNotIn("Traceback", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
