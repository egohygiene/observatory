from __future__ import annotations

import hashlib
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from observatory.health import (  # noqa: E402
    EVIDENCE_SCHEMA,
    HEALTH_SCHEMA,
    adapt_egolint_report,
    build_organization_health,
    load_catalog,
    load_evidence,
    load_json,
    markdown_text,
    validate_evidence,
)
from observatory.health_cli import EGOLINT_REPORT_V1_CONTRACT, main  # noqa: E402
from observatory.intelligence import ContractError, json_text  # noqa: E402

FIXTURES = ROOT / "fixtures" / "health"
CATALOG = FIXTURES / "hygiene.repositories.v1.input.yaml"
OBSERVATORY_EVIDENCE = FIXTURES / "observatory.repository-evidence.input.json"
EGOLINT_REPORT = FIXTURES / "egolint.report.v1.input.json"
EXPECTED = FIXTURES / "expected"
AS_OF = "2026-09-02T12:00:00Z"
CATALOG_COMMIT = "28f9d6c7519d820644572634ba4476614f418d83"
CATALOG_URL = (
    "https://github.com/egohygiene/hygiene/blob/"
    f"{CATALOG_COMMIT}/catalog/repositories.yaml"
)
CATALOG_SHA256 = "e1193c772640ceb8d3d569a1826d3931ee9de64b0a8357a94c9f03fbceab52e5"


def build_fixture_snapshot(evidence: list[dict] | None = None) -> dict:
    return build_organization_health(
        load_catalog(CATALOG),
        evidence if evidence is not None else [load_evidence(OBSERVATORY_EVIDENCE)],
        as_of=AS_OF,
        catalog_url=CATALOG_URL,
        catalog_commit=CATALOG_COMMIT,
        catalog_sha256=CATALOG_SHA256,
    )


def repository(snapshot: dict, full_name: str) -> dict:
    return next(
        item
        for item in snapshot["repositories"]
        if item["repository"]["full_name"] == full_name
    )


class CatalogAndEvidenceTests(unittest.TestCase):
    def test_pinned_catalog_is_exact_and_complete(self) -> None:
        self.assertEqual(
            hashlib.sha256(CATALOG.read_bytes()).hexdigest(), CATALOG_SHA256
        )
        catalog = load_catalog(CATALOG)
        self.assertEqual(len(catalog["repositories"]), 27)
        self.assertEqual(catalog["architecture_release"], "architecture-v0.1.0")

    def test_evidence_normalization_is_order_independent(self) -> None:
        evidence = load_json(OBSERVATORY_EVIDENCE)
        evidence["checks"].reverse()
        normalized = validate_evidence(evidence)
        self.assertEqual(
            [item["id"] for item in normalized["checks"]],
            ["read-model-documentation", "repository-intelligence-alpha"],
        )

    def test_rejects_evidence_without_canonical_provenance(self) -> None:
        evidence = load_json(OBSERVATORY_EVIDENCE)
        evidence["checks"][0]["evidence"] = ["../private/report.json"]
        with self.assertRaisesRegex(ContractError, "absolute HTTP"):
            validate_evidence(evidence)

    def test_rejects_unsupported_evidence_contract(self) -> None:
        evidence = load_json(OBSERVATORY_EVIDENCE)
        evidence["contract_version"] = "2.0.0"
        with self.assertRaisesRegex(ContractError, "unsupported evidence contract"):
            validate_evidence(evidence)

    def test_rejects_empty_or_unstable_check_identity(self) -> None:
        evidence = load_json(OBSERVATORY_EVIDENCE)
        evidence["checks"] = []
        with self.assertRaisesRegex(ContractError, "must not be empty"):
            validate_evidence(evidence)
        evidence = load_json(OBSERVATORY_EVIDENCE)
        evidence["checks"][0]["id"] = "Not stable"
        with self.assertRaisesRegex(ContractError, "canonical lowercase identifier"):
            validate_evidence(evidence)


class HealthCalculationTests(unittest.TestCase):
    def test_catalog_declarations_and_evidence_assessments_remain_separate(
        self,
    ) -> None:
        snapshot = build_fixture_snapshot()
        observatory = repository(snapshot, "egohygiene/observatory")
        self.assertEqual(observatory["declared"]["maturity"], "seed")
        self.assertEqual(observatory["assessment"]["maturity"]["status"], "supported")
        self.assertEqual(
            observatory["assessment"]["conformance"]["status"], "conformant"
        )
        self.assertNotIn("score", observatory["assessment"])

    def test_absent_evidence_remains_unknown(self) -> None:
        snapshot = build_fixture_snapshot()
        relay = repository(snapshot, "egohygiene/relay")
        self.assertEqual(relay["evidence"]["freshness"], "unknown")
        self.assertEqual(relay["assessment"]["maturity"]["status"], "unknown")
        self.assertEqual(relay["assessment"]["conformance"]["status"], "unknown")
        self.assertEqual(snapshot["summary"]["repository_count"], 27)
        self.assertEqual(snapshot["summary"]["unknown_repository_count"], 26)

    def test_expired_evidence_becomes_stale_before_rollup(self) -> None:
        evidence = load_evidence(OBSERVATORY_EVIDENCE)
        evidence["valid_until"] = "2026-09-01T23:59:59Z"
        snapshot = build_fixture_snapshot([evidence])
        observatory = repository(snapshot, "egohygiene/observatory")
        self.assertEqual(observatory["evidence"]["checks"][0]["status"], "stale")
        self.assertEqual(observatory["assessment"]["maturity"]["status"], "stale")
        self.assertEqual(observatory["assessment"]["conformance"]["status"], "stale")

    def test_required_failure_takes_precedence_while_advisory_does_not(self) -> None:
        evidence = load_evidence(OBSERVATORY_EVIDENCE)
        required = next(
            item for item in evidence["checks"] if item["severity"] == "required"
        )
        required["status"] = "fail"
        advisory = next(
            item for item in evidence["checks"] if item["severity"] == "advisory"
        )
        advisory["status"] = "blocked"
        snapshot = build_fixture_snapshot([evidence])
        observatory = repository(snapshot, "egohygiene/observatory")
        self.assertEqual(
            observatory["assessment"]["conformance"]["status"], "non_conformant"
        )
        self.assertEqual(
            observatory["assessment"]["maturity"]["status"], "contradicted"
        )

    def test_rejects_evidence_for_repository_outside_catalog(self) -> None:
        evidence = load_evidence(OBSERVATORY_EVIDENCE)
        evidence["repository"] = "egohygiene/not-in-catalog"
        with self.assertRaisesRegex(ContractError, "absent from the Hygiene catalog"):
            build_fixture_snapshot([evidence])

    def test_rejects_future_observation(self) -> None:
        evidence = load_evidence(OBSERVATORY_EVIDENCE)
        evidence["observed_at"] = "2026-09-03T00:00:00Z"
        evidence["valid_until"] = "2026-09-30T00:00:00Z"
        with self.assertRaisesRegex(ContractError, "later than snapshot"):
            build_fixture_snapshot([evidence])

    def test_rejects_competing_check_identity_instead_of_picking_a_winner(self) -> None:
        evidence = load_evidence(OBSERVATORY_EVIDENCE)
        newer = deepcopy(evidence)
        newer["observed_at"] = "2026-09-02T00:00:00Z"
        with self.assertRaisesRegex(ContractError, "duplicate check identity"):
            build_fixture_snapshot([evidence, newer])

    def test_snapshot_is_deterministic_and_markdown_is_explicit(self) -> None:
        first = build_fixture_snapshot()
        second = build_fixture_snapshot()
        self.assertEqual(json_text(first), json_text(second))
        report = markdown_text(first)
        self.assertIn("[egohygiene/observatory]", report)
        self.assertIn("No numeric score is calculated.", report)


class EgolintAdapterTests(unittest.TestCase):
    def test_maps_v1_findings_report_without_reinterpreting_findings(self) -> None:
        report = load_json(EGOLINT_REPORT)
        evidence = adapt_egolint_report(
            report,
            repository="egohygiene/empathy",
            represented_commit="a" * 40,
            valid_until="2027-01-01T00:00:00Z",
            source_url=(
                "https://github.com/egohygiene/egolint/blob/"
                "4b98b30eb3a574c81986fb9be585c4935f585f65/"
                "tests/fixtures/compatibility/empathy-v1/report.json"
            ),
            source_sha256=hashlib.sha256(EGOLINT_REPORT.read_bytes()).hexdigest(),
            producer_version="0.1.0-alpha.1",
            contract_url=EGOLINT_REPORT_V1_CONTRACT,
        )
        self.assertEqual(evidence["schema"], EVIDENCE_SCHEMA)
        self.assertEqual(evidence["checks"][0]["status"], "fail")
        self.assertEqual(evidence["checks"][0]["assesses"], ["conformance"])
        self.assertEqual(evidence["checks"][0]["id"], "egolint:holistic")

    def test_rejects_mutating_egolint_operation(self) -> None:
        report = load_json(EGOLINT_REPORT)
        report["operation"] = "fix"
        with self.assertRaisesRegex(ContractError, "read-only"):
            adapt_egolint_report(
                report,
                repository="egohygiene/empathy",
                represented_commit="a" * 40,
                valid_until="2027-01-01T00:00:00Z",
                source_url="https://example.com/report.json",
                source_sha256="b" * 64,
                producer_version="0.1.0-alpha.1",
                contract_url=EGOLINT_REPORT_V1_CONTRACT,
            )


class HealthCliAndContractTests(unittest.TestCase):
    def test_build_and_adapt_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    main(
                        [
                            "build",
                            "--catalog",
                            str(CATALOG),
                            "--catalog-url",
                            CATALOG_URL,
                            "--catalog-commit",
                            CATALOG_COMMIT,
                            "--evidence",
                            str(OBSERVATORY_EVIDENCE),
                            "--as-of",
                            AS_OF,
                            "--output",
                            str(output),
                        ]
                    ),
                    0,
                )
            self.assertTrue((output / "organization-health.json").is_file())
            self.assertTrue((output / "organization-health.md").is_file())

            adapted = output / "egolint-evidence.json"
            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    main(
                        [
                            "adapt-egolint",
                            "--report",
                            str(EGOLINT_REPORT),
                            "--repository",
                            "egohygiene/empathy",
                            "--represented-commit",
                            "a" * 40,
                            "--valid-until",
                            "2027-01-01T00:00:00Z",
                            "--source-url",
                            "https://example.com/report.json",
                            "--producer-version",
                            "0.1.0-alpha.1",
                            "--output",
                            str(adapted),
                        ]
                    ),
                    0,
                )
            self.assertEqual(load_json(adapted)["schema"], EVIDENCE_SCHEMA)

    def test_contract_error_returns_stable_nonzero_exit(self) -> None:
        with redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(
                main(
                    [
                        "build",
                        "--catalog",
                        "missing-catalog.json",
                        "--catalog-url",
                        CATALOG_URL,
                        "--catalog-commit",
                        CATALOG_COMMIT,
                        "--as-of",
                        AS_OF,
                        "--output",
                        "unused",
                    ]
                ),
                2,
            )
        self.assertIn("cannot read JSON", errors.getvalue())

    def test_schemas_pin_public_identifiers(self) -> None:
        evidence_schema = load_json(
            ROOT / "schemas" / "repository-evidence.v1.schema.json"
        )
        health_schema = load_json(
            ROOT / "schemas" / "organization-health.v1.schema.json"
        )
        self.assertEqual(
            evidence_schema["properties"]["schema"]["const"], EVIDENCE_SCHEMA
        )
        self.assertEqual(health_schema["properties"]["schema"]["const"], HEALTH_SCHEMA)

    def test_contract_locks_match_adapter_and_catalog_fixtures(self) -> None:
        hygiene_lock = load_json(
            ROOT / "contracts" / "hygiene.repository-catalog.v1.lock.json"
        )
        self.assertEqual(hygiene_lock["source_commit"], CATALOG_COMMIT)
        self.assertEqual(hygiene_lock["sources"][0]["sha256"], CATALOG_SHA256)
        egolint_lock = load_json(ROOT / "contracts" / "egolint.report.v1.lock.json")
        self.assertIn(egolint_lock["source_commit"], EGOLINT_REPORT_V1_CONTRACT)


if __name__ == "__main__":
    unittest.main()
