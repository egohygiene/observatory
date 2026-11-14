"""Synthetic diagnosis metadata/state and non-disclosure integration contracts."""
from contextlib import redirect_stderr
from copy import deepcopy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from observatory.diagnoses import build_diagnosis_view, validate_view, attach_to_snapshot, EXTENSION
from observatory.diagnoses_cli import main
from observatory import public_reviews as shared
from observatory.intelligence import build_repository_snapshot, build_fleet_snapshot

FIXTURES = ROOT / "fixtures/diagnoses"
AS_OF = "2026-11-14T04:00:00Z"


class DiagnosisObservationTests(unittest.TestCase):
    def setUp(self):
        self.wrappers = json.loads((FIXTURES / "observations.json").read_text())
        self.targets = json.loads((FIXTURES / "targets.json").read_text())

    def build(self, wrappers=None, targets=None, as_of=AS_OF):
        return build_diagnosis_view(self.wrappers if wrappers is None else wrappers,
            repositories=self.targets if targets is None else targets, as_of=as_of)

    def observed(self, view):
        return next(row for row in view["repositories"] if row["repository"]["full_name"] == "egohygiene/observatory")

    def test_synthetic_expected_schema_seal_and_explicit_policy_gap(self):
        view = self.build()
        self.assertEqual(view, json.loads((FIXTURES / "expected.json").read_text()))
        schema = json.loads((ROOT / "schemas/fleet-diagnoses.v1.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(view)
        self.assertEqual(validate_view(view), view)
        self.assertEqual(view["policy"]["status"], "unavailable")

    def test_private_restricted_pending_and_withheld_payloads_do_not_affect_public_bytes(self):
        expected = self.build()
        wrappers = deepcopy(self.wrappers)
        wrappers[0]["evidence"]["records"][-1] = {"sensitivity":"restricted", "malformed":["synthetic-private-canary", None]}
        wrappers[0]["evidence"]["records"].append({"sensitivity":"public", "publication":{"status":"pending"}, "id":"another-private-canary"})
        wrappers[1]["evidence"]["records"] = {"hidden":"do-not-parse-private-canary"}
        wrappers.append({"visibility":"private", "repository":"egohygiene/private-canary", "evidence":True})
        self.assertEqual(expected, self.build(wrappers))
        self.assertNotIn("private-canary", json.dumps(expected))
        self.assertEqual(expected, self.build(targets=self.targets + [{"repository":"egohygiene/private-canary", "represented_commit":None}]))

    def test_restricted_duplicate_keys_are_not_validated_or_counted(self):
        raw = shared.parse(b'{"sensitivity":"restricted","id":"private-canary","id":"other-private-canary"}')
        self.wrappers[0]["evidence"]["records"].append(raw)
        self.assertEqual(self.build(), json.loads((FIXTURES / "expected.json").read_text()))

    def test_independent_states_are_preserved_without_health_or_truth_upgrade(self):
        nodes = self.observed(self.build())["nodes"]
        open_record = next(n["metadata"] for n in nodes if n["metadata"]["status"] == "open")
        self.assertEqual((open_record["reproduction"],open_record["root_cause"],open_record["remediation"],open_record["validation"],open_record["conformance"]),
                         ("reproduced","suspected","not-authorized","blocked","valid"))
        superseded = next(n["metadata"] for n in nodes if n["metadata"]["status"] == "superseded")
        self.assertEqual(superseded["validation"], "failed")
        self.assertTrue(all(n["content_integrity"] == "unverified-source-claim" for n in nodes))

    def test_expiry_revision_and_missing_collection_remain_explicit(self):
        view = self.build(as_of="2026-11-16T04:00:00Z")
        observed = self.observed(view)
        self.assertEqual(observed["observation_freshness"], "stale")
        self.assertIn("different", {node["revision_status"] for node in observed["nodes"]})
        rows = {row["repository"]["full_name"]:row for row in view["repositories"]}
        self.assertEqual(rows["egohygiene/relay"]["collection"], "withheld")
        self.assertEqual(rows["egohygiene/mantle"]["collection"], "unavailable")
        self.wrappers[0]["evidence"]["represented_commit"] = "b" * 40
        self.assertEqual(self.observed(self.build())["collection_revision"], "other-revision-only")

    def test_absence_in_later_capture_does_not_resolve_historical_records(self):
        later = deepcopy(self.wrappers[0]); later["evidence"].update(observed_at="2026-11-14T03:30:00Z",collection="observed-empty",records=[])
        row = self.observed(self.build(self.wrappers + [later]))
        self.assertEqual(row["public_record_count"], 0)
        self.assertEqual(row["collection"], "observed-empty")
        self.assertEqual(len(row["observations"][0]["records"]), 3)
        self.assertEqual(row["observations"][0]["records"][0]["status"], "open")

    def test_order_duplicate_capture_and_record_are_deterministic(self):
        expected = self.build(); original = deepcopy(self.wrappers)
        self.assertEqual(expected, self.build(list(reversed(self.wrappers)),list(reversed(self.targets))))
        self.assertEqual(original,self.wrappers)
        self.wrappers[0]["evidence"]["records"].append(deepcopy(self.wrappers[0]["evidence"]["records"][0]))
        self.assertEqual(expected,self.build(self.wrappers + [deepcopy(self.wrappers[0])]))

    def test_conflicts_malformed_metadata_body_and_wrong_pin_fail_closed(self):
        mutations=[lambda d:d.update(body="synthetic-private-canary"),
            lambda d:d["contract"].update(version="2.0.0"),
            lambda d:d.update(root_cause="structurally-valid-so-confirmed"),
            lambda d:d["hypothesis_counts"].update(open=True),
            lambda d:d.update(context={"component":"raw-private-canary"})]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                wrappers=deepcopy(self.wrappers);mutate(wrappers[0]["evidence"]["records"][0])
                with self.assertRaises(ValueError) as caught:self.build(wrappers)
                self.assertNotIn("private-canary",str(caught.exception))
        conflict=deepcopy(self.wrappers[0]);conflict["evidence"]["records"][0]["validation"]="passed"
        with self.assertRaises(ValueError):self.build(self.wrappers+[conflict])

    def test_private_scope_relationship_drops_record_before_identity_or_digest(self):
        wrappers=deepcopy(self.wrappers)
        wrappers[0]["evidence"]["records"][0]["related"]=[{"relation":"issue","target":"https://github.com/egohygiene/private-canary/issues/1"}]
        expected=deepcopy(self.wrappers);expected[0]["evidence"]["records"].pop(0)
        self.assertEqual(self.build(expected),self.build(wrappers))

    def test_resealed_forged_count_or_truth_cannot_validate(self):
        model=self.build();self.observed(model)["public_record_count"]=100
        model=shared.seal({k:v for k,v in model.items() if k!="digest"})
        with self.assertRaises(ValueError):validate_view(model)

    def test_canonical_source_cannot_change_repository_or_alias_distinct_ids(self):
        for target in ("https://github.com/egohygiene/hygiene/blob/"+"a"*40+"/record.md",
                       self.wrappers[0]["evidence"]["records"][1]["canonical_url"]):
            with self.subTest(target=target):
                wrappers=deepcopy(self.wrappers)
                wrappers[0]["evidence"]["records"][0]["canonical_url"]=target
                with self.assertRaises(ValueError):self.build(wrappers)

    def test_repository_intelligence_composition_preserves_existing_graph_and_queries(self):
        projection=json.loads((ROOT/"fixtures/repository-intelligence/observatory-active.input.json").read_text())
        snapshot=build_repository_snapshot(projection); before=deepcopy(snapshot)
        view=self.build(targets=[self.targets[0]])
        composed=attach_to_snapshot(snapshot,view)
        self.assertEqual(snapshot,before)
        self.assertEqual(composed["graph"],snapshot["graph"])
        self.assertEqual(composed["views"],snapshot["views"])
        self.assertEqual(composed["extensions"][EXTENSION],view)
        self.assertNotEqual(composed["snapshot_id"],snapshot["snapshot_id"])
        Draft202012Validator(json.loads((ROOT/"schemas/repository-intelligence-read-model.v1.schema.json").read_text())).validate(composed)
        build_fleet_snapshot([composed])
        bad=deepcopy(snapshot);bad["represented_commit"]="d"*40
        with self.assertRaises(ValueError):attach_to_snapshot(bad,view)

    def test_canonical_record_fragment_alias_is_rejected_without_changing_related_links(self):
        wrappers=deepcopy(self.wrappers)
        wrappers[0]["evidence"]["records"][1]["canonical_url"] = wrappers[0]["evidence"]["records"][0]["canonical_url"] + "#same-file-alias"
        with self.assertRaises(ValueError):self.build(wrappers)
        wrappers=deepcopy(self.wrappers)
        wrappers[0]["evidence"]["records"][0]["related"][0]["target"] += "#public-evidence-section"
        self.assertEqual(self.observed(self.build(wrappers))["public_record_count"],3)

    def test_cli_output_is_explicit_new_and_errors_do_not_echo_rejected_content(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/"view.json"
            args=["--targets",str(FIXTURES/"targets.json"),"--evidence",str(FIXTURES/"observations.json"),"--as-of",AS_OF,"--output",str(output)]
            self.assertEqual(main(args),0)
            self.assertEqual(json.loads(output.read_text()),self.build())
            before=output.read_bytes();stderr=io.StringIO()
            with redirect_stderr(stderr):self.assertEqual(main(args),2)
            self.assertEqual(output.read_bytes(),before)
            self.assertNotIn("Traceback",stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
