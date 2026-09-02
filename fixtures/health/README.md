# Organization-health fixtures

The catalog fixture is an exact copy of Hygiene's JSON-compatible YAML catalog
at commit `28f9d6c7519d820644572634ba4476614f418d83`. Its digest is pinned in
`contracts/hygiene.repository-catalog.v1.lock.json`.

The Observatory evidence record is reviewed synthetic input grounded in the
merged Repository Intelligence pull request. It exists to exercise a current,
supported result without claiming that a live collector already runs. The
Egolint report is an exact compatibility fixture from Egolint commit
`4b98b30eb3a574c81986fb9be585c4935f585f65` and proves the first real validator
adapter contract offline. Its derived Empathy evidence is intentionally expired
so the golden outputs visibly preserve stale evidence instead of presenting an
old finding as current.

Golden outputs use an explicit `2026-09-02T12:00:00Z` evaluation time. They are
examples and compatibility evidence, not a live organization status report.
