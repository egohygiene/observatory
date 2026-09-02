# egohygiene organization health

- Snapshot: `organization-health:sha256:4414b2c8cf3921c61b4cc79cf859167ae5b499f428f152e7aa8feee1a7af725e`
- As of: `2026-09-02T12:00:00Z`
- Catalog: [architecture-v0.1.0](https://github.com/egohygiene/hygiene/blob/28f9d6c7519d820644572634ba4476614f418d83/catalog/repositories.yaml) at `28f9d6c7519d820644572634ba4476614f418d83`
- Catalog freshness: `unknown` — the catalog contract does not declare a validity window
- Evidence records: `2`

The declared maturity column comes from Hygiene. The evidence columns are Observatory rollups; they never replace the declaration or hide missing data behind a percentage.

| Repository | Lifecycle | Declared maturity | Maturity evidence | Conformance | Evidence freshness |
| --- | --- | --- | --- | --- | --- |
| [egohygiene/.github](https://github.com/egohygiene/.github) | incubating | light-foundation | unknown | unknown | unknown |
| [egohygiene/aether](https://github.com/egohygiene/aether) | active | active | unknown | unknown | unknown |
| [egohygiene/akashic](https://github.com/egohygiene/akashic) | active | active | unknown | unknown | unknown |
| [egohygiene/aniflow](https://github.com/egohygiene/aniflow) | active | active | unknown | unknown | unknown |
| [egohygiene/athena](https://github.com/egohygiene/athena) | active | active-collection | unknown | unknown | unknown |
| [egohygiene/beacon](https://github.com/egohygiene/beacon) | seed | seed | unknown | unknown | unknown |
| [egohygiene/egohygiene](https://github.com/egohygiene/egohygiene) | active | active-private | unknown | unknown | unknown |
| [egohygiene/egolint](https://github.com/egohygiene/egolint) | incubating | early-implementation | unknown | unknown | unknown |
| [egohygiene/empathy](https://github.com/egohygiene/empathy) | transition | transition | unknown | stale | stale |
| [egohygiene/filament](https://github.com/egohygiene/filament) | architecture-first | provisional-architecture | unknown | unknown | unknown |
| [egohygiene/flow](https://github.com/egohygiene/flow) | architecture-first | architecture-first | unknown | unknown | unknown |
| [egohygiene/holon](https://github.com/egohygiene/holon) | seed | seed | unknown | unknown | unknown |
| [egohygiene/hygiene](https://github.com/egohygiene/hygiene) | seed | seed | unknown | unknown | unknown |
| [egohygiene/identity](https://github.com/egohygiene/identity) | seed | seed | unknown | unknown | unknown |
| [egohygiene/mantle](https://github.com/egohygiene/mantle) | active | active | unknown | unknown | unknown |
| [egohygiene/mindcap](https://github.com/egohygiene/mindcap) | active | active | unknown | unknown | unknown |
| [egohygiene/mindgarden](https://github.com/egohygiene/mindgarden) | seed | seed | unknown | unknown | unknown |
| [egohygiene/observatory](https://github.com/egohygiene/observatory) | seed | seed | supported | conformant | current |
| [egohygiene/optiflow](https://github.com/egohygiene/optiflow) | active | active-read-only | unknown | unknown | unknown |
| [egohygiene/pace](https://github.com/egohygiene/pace) | seed | seed | unknown | unknown | unknown |
| [egohygiene/realm](https://github.com/egohygiene/realm) | seed | seed-with-staged-source | unknown | unknown | unknown |
| [egohygiene/reflector](https://github.com/egohygiene/reflector) | active | active | unknown | unknown | unknown |
| [egohygiene/relay](https://github.com/egohygiene/relay) | seed | seed | unknown | unknown | unknown |
| [egohygiene/renderflow](https://github.com/egohygiene/renderflow) | active | active | unknown | unknown | unknown |
| [egohygiene/sanctuary](https://github.com/egohygiene/sanctuary) | incubating | provisional-contract | unknown | unknown | unknown |
| [egohygiene/store](https://github.com/egohygiene/store) | active | active | unknown | unknown | unknown |
| [egohygiene/website](https://github.com/egohygiene/website) | transition | active-rename-pending | unknown | unknown | unknown |

## Calculation rules

Only required checks affect a rollup. The effective precedence is fail, blocked, stale, unknown, partial, pass, then not applicable. Expired evidence is reported as stale before rollup. Maturity evidence maps a failure to `contradicted` and a pass to `supported`; conformance maps them to `non_conformant` and `conformant`. A repository without qualifying evidence remains `unknown`. Advisory checks stay visible in JSON but do not change the rollup. No numeric score is calculated.
