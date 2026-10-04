# Repository Intelligence fixtures

These inputs let Observatory, Holon, and Relay develop without live GitHub access.

- `relay-complete-quest.input.json` is copied byte-for-byte from Hygiene's complete-quest compatibility fixture at immutable revision `5e0602265b6ac5e5165b89f418e55a3fd12f8a64`. Its SHA-256 is `7571348da763a9ec60aa8af60e2290fbf6d153da39ef9760d8c71ab90651c8db`.
- `observatory-active.input.json` is an Observatory-owned fixture that exercises current, stale, unknown, inferred, blocked, and cross-repository dependency states.

Both inputs claim `egohygiene.repository-intelligence/v1` compatibility. Hygiene remains the contract owner; these files are test evidence, not policy copies.


`coverage/*.json` are byte-identical copies of the eight Hygiene alpha.2
fixtures pinned in `contracts/hygiene.repository-intelligence.alpha2.lock.json`.
They exercise roadmap-only, provider-denied, partial, failed, observed-empty,
explicit not-applicable, stale, and full collection. The fixture names describe
synthetic cases, never a claim about live repositories.

`fixtures/expected/coverage` contains their repository snapshots, three extracted
roadmap-only views, and a mixed alpha.1/alpha.2-input fleet snapshot. Run
`scripts/verify_fixtures.py` to compare all 15 Intelligence golden artifacts.
The existing alpha.1 input bytes and their original lock remain unchanged;
expected read models move to alpha.2 with unknown legacy completeness.
