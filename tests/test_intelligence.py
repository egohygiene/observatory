from __future__ import annotations

import hashlib
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from observatory.cli import main
from observatory.intelligence import (
    COMPARE_SCHEMA,
    FLEET_SCHEMA,
    READ_MODEL_SCHEMA,
    VIEW_NAMES,
    VIEW_SCHEMA,
    ContractError,
    build_fleet_snapshot,
    build_repository_snapshot,
    compare_snapshots,
    extract_view,
    json_text,
    load_json,
    load_projection,
)

FIXTURES = ROOT / "fixtures" / "repository-intelligence"
EXPECTED = ROOT / "fixtures" / "expected"
RELAY_FIXTURE = FIXTURES / "relay-complete-quest.input.json"
OBSERVATORY_FIXTURE = FIXTURES / "observatory-active.input.json"


def entity(snapshot: dict, identifier: str) -> dict:
    return next(item for item in snapshot["graph"]["entities"] if item["id"] == identifier)


def roadmap_step(snapshot: dict, key: str) -> dict:
    return next(
        item for item in snapshot["views"]["roadmap"]["steps"] if item["entity"]["key"] == key
    )


class RepositorySnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.relay_projection = load_projection(RELAY_FIXTURE)
        cls.observatory_projection = load_projection(OBSERVATORY_FIXTURE)
        cls.relay = build_repository_snapshot(cls.relay_projection)
        cls.observatory = build_repository_snapshot(cls.observatory_projection)

    def test_hygiene_fixture_is_an_exact_pinned_copy(self) -> None:
        checksum = hashlib.sha256(RELAY_FIXTURE.read_bytes()).hexdigest()
        self.assertEqual(
            checksum,
            "7571348da763a9ec60aa8af60e2290fbf6d153da39ef9760d8c71ab90651c8db",
        )

    def test_complete_chain_reaches_decision_delivery_and_deployment(self) -> None:
        quest = roadmap_step(self.relay, "REL-RM-003")
        self.assertEqual([item["key"] for item in quest["informed_by"]], ["ADR-007"])
        self.assertEqual([item["key"] for item in quest["tracked_by"]], ["27"])
        self.assertEqual(
            [item["key"] for item in quest["evidence"]],
            ["bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"],
        )

        decision = self.relay["views"]["decisions"]["decisions"][0]
        self.assertEqual(decision["entity"]["key"], "ADR-007")
        self.assertEqual([item["kind"] for item in decision["verified_by"]], ["check"])

        release = self.relay["views"]["releases"]["releases"][0]
        self.assertEqual(
            [item["kind"] for item in release["includes"]], ["commit", "pull_request"]
        )
        self.assertEqual([item["kind"] for item in release["deployments"]], ["deployment"])

    def test_all_initial_page_views_are_present_and_extractable(self) -> None:
        self.assertEqual(tuple(self.relay["views"]), VIEW_NAMES)
        for name in VIEW_NAMES:
            with self.subTest(view=name):
                projection = extract_view(self.relay, name)
                self.assertEqual(projection["schema"], VIEW_SCHEMA)
                self.assertEqual(projection["view"], name)
                self.assertEqual(projection["scope"], "repository")
                self.assertEqual(projection["subject"], "egohygiene/relay")

    def test_stale_unknown_inferred_and_blocked_states_remain_explicit(self) -> None:
        self.assertEqual(self.observatory["coverage"]["status"], "unknown")
        foundation = roadmap_step(self.observatory, "OBS-Q02")
        self.assertEqual(foundation["readiness"]["value"], "blocked")
        self.assertEqual(foundation["blocked_by"][0]["freshness"], "stale")
        future = roadmap_step(self.observatory, "OBS-Q03")
        self.assertEqual(future["readiness"]["value"], "unknown")
        inferred = next(
            item
            for item in self.observatory["graph"]["relationships"]
            if item["id"] == "relationship:issue-7-implements-foundation"
        )
        self.assertEqual(inferred["assertion"], "inferred")
        self.assertIsNone(self.observatory["views"]["health"]["score"])
        self.assertGreater(self.relay["coverage"]["freshness"]["not_applicable"], 0)

    def test_now_distinguishes_dependencies_from_actual_blockers(self) -> None:
        blockers = self.observatory["views"]["now"]["blockers"]
        self.assertEqual([item["type"] for item in blockers], ["blocks"])
        self.assertEqual(blockers[0]["source"]["key"], "1")

    def test_ready_work_is_an_inference_with_reasons_preserved(self) -> None:
        projection = deepcopy(self.observatory_projection)
        projection["relationships"] = [
            item
            for item in projection["relationships"]
            if item["type"] != "blocks"
        ]
        next(item for item in projection["entities"] if item["key"] == "OBS-Q02")["state"][
            "value"
        ] = "complete"
        next(item for item in projection["entities"] if item["key"] == "OBS-Q03")[
            "freshness"
        ] = "current"
        result = build_repository_snapshot(projection)
        ready = result["views"]["now"]["next_ready"]
        self.assertEqual([item["key"] for item in ready], ["OBS-Q03"])
        self.assertEqual(roadmap_step(result, "OBS-Q03")["readiness"]["assertion"], "inferred")

    def test_history_is_grouped_at_release_boundaries(self) -> None:
        chapters = self.relay["views"]["journey"]["chapters"]
        self.assertEqual(len(chapters), 2)
        self.assertEqual(chapters[0]["boundary"]["kind"], "release")
        self.assertTrue(chapters[1]["title"].startswith("After "))

    def test_every_entity_keeps_a_canonical_source_link(self) -> None:
        for item in self.observatory["graph"]["entities"]:
            with self.subTest(entity=item["id"]):
                self.assertTrue(item["canonical_url"].startswith("https://"))
                self.assertTrue(item["provenance"])

    def test_build_is_independent_of_collection_order(self) -> None:
        reordered = deepcopy(self.relay_projection)
        for collection in ("sources", "entities", "relationships", "events", "redactions"):
            reordered[collection].reverse()
        self.assertEqual(build_repository_snapshot(reordered), self.relay)

    def test_serialization_is_stable_and_has_a_final_newline(self) -> None:
        first = json_text(self.relay)
        second = json_text(build_repository_snapshot(self.relay_projection))
        self.assertEqual(first, second)
        self.assertTrue(first.endswith("\n"))


class FleetAndCompareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.relay = build_repository_snapshot(load_projection(RELAY_FIXTURE))
        cls.observatory = build_repository_snapshot(load_projection(OBSERVATORY_FIXTURE))

    def test_fleet_snapshot_is_deterministic_and_context_preserving(self) -> None:
        first = build_fleet_snapshot([self.relay, self.observatory])
        second = build_fleet_snapshot([self.observatory, self.relay])
        self.assertEqual(first, second)
        self.assertEqual(first["schema"], FLEET_SCHEMA)
        self.assertEqual(
            [item["repository"]["repository"] for item in first["repositories"]],
            ["egohygiene/observatory", "egohygiene/relay"],
        )
        repository_groups = first["views"]["roadmap"]["repositories"]
        self.assertEqual(len(repository_groups), 2)

    def test_fleet_rejects_duplicate_repository_snapshots(self) -> None:
        with self.assertRaisesRegex(ContractError, "more than one snapshot"):
            build_fleet_snapshot([self.relay, self.relay])

    def test_compare_reports_source_changes_without_claiming_causality(self) -> None:
        projection = load_projection(RELAY_FIXTURE)
        projection["represented_commit"] = "dddddddddddddddddddddddddddddddddddddddd"
        projection["projection_id"] = (
            "egohygiene/relay@dddddddddddddddddddddddddddddddddddddddd"
        )
        next(item for item in projection["entities"] if item["key"] == "REL-RM-003")[
            "title"
        ] = "Publish the stable evidence assembly"
        after = build_repository_snapshot(projection)
        comparison = compare_snapshots(self.relay, after)
        self.assertEqual(comparison["schema"], COMPARE_SCHEMA)
        changed = comparison["entities"]["changed"]
        self.assertEqual(len(changed), 1)
        self.assertEqual(changed[0]["fields"], ["title"])
        roadmap = next(item for item in comparison["views"] if item["view"] == "roadmap")
        self.assertTrue(roadmap["changed"])


class DefensiveBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.projection = load_json(RELAY_FIXTURE)

    def test_rejects_unsupported_contract_version(self) -> None:
        self.projection["contract_version"] = "2.0.0"
        with self.assertRaisesRegex(ContractError, "unsupported"):
            build_repository_snapshot(self.projection)

    def test_rejects_duplicate_entity_ids(self) -> None:
        self.projection["entities"].append(deepcopy(self.projection["entities"][0]))
        with self.assertRaisesRegex(ContractError, "duplicate"):
            build_repository_snapshot(self.projection)

    def test_rejects_dangling_relationships(self) -> None:
        self.projection["relationships"][0]["target"] = "ri:egohygiene/relay:issue:404"
        with self.assertRaisesRegex(ContractError, "dangling"):
            build_repository_snapshot(self.projection)

    def test_rejects_dangling_provenance(self) -> None:
        self.projection["entities"][0]["provenance"] = ["source:missing"]
        with self.assertRaisesRegex(ContractError, "unknown sources"):
            build_repository_snapshot(self.projection)

    def test_rejects_noncanonical_source_urls(self) -> None:
        self.projection["sources"][0]["url"] = "../private/session.json"
        with self.assertRaisesRegex(ContractError, "absolute HTTP"):
            build_repository_snapshot(self.projection)

    def test_rejects_unknown_assertion_categories(self) -> None:
        self.projection["relationships"][0]["assertion"] = "probably"
        with self.assertRaisesRegex(ContractError, "unsupported assertion"):
            build_repository_snapshot(self.projection)

    def test_rejects_non_string_provenance(self) -> None:
        self.projection["entities"][0]["provenance"] = [{"source": "roadmap"}]
        with self.assertRaisesRegex(ContractError, "must be a non-empty string"):
            build_repository_snapshot(self.projection)


class CliTests(unittest.TestCase):
    def test_build_query_compare_and_validate_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    main(
                        [
                            "build",
                            "--input",
                            str(RELAY_FIXTURE),
                            "--input",
                            str(OBSERVATORY_FIXTURE),
                            "--output",
                            str(output),
                        ]
                    ),
                    0,
                )
            relay = output / "repositories" / "egohygiene--relay.json"
            self.assertTrue(relay.is_file())
            self.assertTrue((output / "fleet.json").is_file())

            now = output / "now.json"
            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    main(
                        [
                            "query",
                            "--snapshot",
                            str(relay),
                            "--view",
                            "now",
                            "--output",
                            str(now),
                        ]
                    ),
                    0,
                )
            self.assertEqual(load_json(now)["view"], "now")

            compare = output / "compare.json"
            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    main(
                        [
                            "compare",
                            "--before",
                            str(relay),
                            "--after",
                            str(relay),
                            "--output",
                            str(compare),
                        ]
                    ),
                    0,
                )
            self.assertEqual(load_json(compare)["schema"], COMPARE_SCHEMA)

            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["validate", "--input", str(RELAY_FIXTURE)]), 0)

    def test_invalid_input_returns_a_nonzero_contract_exit(self) -> None:
        error = io.StringIO()
        with redirect_stderr(error):
            result = main(["validate", "--input", str(ROOT / "missing.json")])
        self.assertEqual(result, 2)
        self.assertIn("cannot read JSON", error.getvalue())


class CheckedContractTests(unittest.TestCase):
    def test_schemas_are_parseable_and_pin_the_public_identifiers(self) -> None:
        expected = {
            "repository-intelligence-read-model.v1.schema.json": READ_MODEL_SCHEMA,
            "repository-intelligence-fleet.v1.schema.json": FLEET_SCHEMA,
            "repository-intelligence-view.v1.schema.json": VIEW_SCHEMA,
            "repository-intelligence-compare.v1.schema.json": COMPARE_SCHEMA,
        }
        for filename, schema_identifier in expected.items():
            with self.subTest(schema=filename):
                schema = load_json(ROOT / "schemas" / filename)
                self.assertEqual(schema["properties"]["schema"]["const"], schema_identifier)
                self.assertFalse(schema["additionalProperties"])

    def test_expected_snapshots_match_current_generation(self) -> None:
        expected_relay = load_json(EXPECTED / "egohygiene--relay.repository.json")
        expected_observatory = load_json(EXPECTED / "egohygiene--observatory.repository.json")
        expected_fleet = load_json(EXPECTED / "fleet.json")
        relay = build_repository_snapshot(load_projection(RELAY_FIXTURE))
        observatory = build_repository_snapshot(load_projection(OBSERVATORY_FIXTURE))
        self.assertEqual(relay, expected_relay)
        self.assertEqual(observatory, expected_observatory)
        self.assertEqual(build_fleet_snapshot([relay, observatory]), expected_fleet)


if __name__ == "__main__":
    unittest.main()
