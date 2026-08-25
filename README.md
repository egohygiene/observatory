# Observatory

🔭 Organization visibility, maturity tracking, and platform observability for Ego Hygiene.

Observatory turns validated repository evidence into deterministic, provenance-aware read models. It answers Repository Intelligence questions without becoming the source of roadmap intent, decision authority, Git history, GitHub state, validation policy, or release truth.

## Repository Intelligence alpha

The first executable slice consumes the pinned Hygiene `egohygiene.repository-intelligence/v1` projection and produces:

- a self-contained repository graph/read model;
- query projections for Roadmap, Decisions, Journey, Now, Dependencies, Health, Releases, Work, and Search;
- a deterministic fleet snapshot that preserves repository context;
- a before/after Compare projection; and
- fully offline fixtures for Relay and Holon development.

The implementation is dependency-free Python 3.11+ and performs no network access. Hygiene owns the input contract and vocabulary. Egolint owns semantic validation. Observatory rejects unsupported or unsafe inputs, then indexes and composes the accepted evidence.

## Quick start

```bash
python3 -m pip install --editable .

observatory-intelligence validate \
  --input "fixtures/repository-intelligence/relay-complete-quest.input.json"

observatory-intelligence build \
  --input "fixtures/repository-intelligence/relay-complete-quest.input.json" \
  --input "fixtures/repository-intelligence/observatory-active.input.json" \
  --output "build/repository-intelligence"

observatory-intelligence query \
  --snapshot "build/repository-intelligence/repositories/egohygiene--relay.json" \
  --view "roadmap" \
  --output "build/relay-roadmap.json"

observatory-intelligence compare \
  --before "fixtures/expected/egohygiene--relay.repository.json" \
  --after "build/repository-intelligence/repositories/egohygiene--relay.json" \
  --output "build/relay-compare.json"
```

`build` writes one file under `repositories/` per repository plus `fleet.json`. Output ordering, timestamps, and identifiers come entirely from pinned input; the ambient wall clock is never used.

## Contracts and fixtures

- [Read-model and query contract](docs/repository-intelligence-read-model.md)
- [Repository read-model schema](schemas/repository-intelligence-read-model.v1.schema.json)
- [Fleet snapshot schema](schemas/repository-intelligence-fleet.v1.schema.json)
- [View envelope schema](schemas/repository-intelligence-view.v1.schema.json)
- [Compare schema](schemas/repository-intelligence-compare.v1.schema.json)
- [Pinned Hygiene contract lock](contracts/hygiene.repository-intelligence.v1.lock.json)
- [Offline fixture provenance](fixtures/repository-intelligence/README.md)

## Verification

```bash
python3 -m unittest discover \
  --start-directory "tests" \
  --pattern "test_*.py" \
  --verbose

python3 "scripts/verify_fixtures.py"
```

The checked-in snapshots are intentional consumer fixtures. Any semantic change must update the contract version or remain demonstrably compatible, update the golden artifacts, and explain its downstream impact.
