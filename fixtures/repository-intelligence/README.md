# Repository Intelligence fixtures

These inputs let Observatory, Holon, and Relay develop without live GitHub access.

- `relay-complete-quest.input.json` is copied byte-for-byte from Hygiene's complete-quest compatibility fixture at immutable revision `5e0602265b6ac5e5165b89f418e55a3fd12f8a64`. Its SHA-256 is `7571348da763a9ec60aa8af60e2290fbf6d153da39ef9760d8c71ab90651c8db`.
- `observatory-active.input.json` is an Observatory-owned fixture that exercises current, stale, unknown, inferred, blocked, and cross-repository dependency states.

Both inputs claim `egohygiene.repository-intelligence/v1` compatibility. Hygiene remains the contract owner; these files are test evidence, not policy copies.
