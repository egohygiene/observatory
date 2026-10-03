"""Regression boundary for unavailable data, honest emptiness and pinned migration."""
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from observatory.cli import main
from observatory.intelligence import (
    COLLECTION_DOMAINS, VIEW_NAMES, ContractError, build_repository_snapshot,
    build_fleet_snapshot, compare_snapshots, extract_view, json_text, load_json,
)
FIXTURES = ROOT / 'fixtures/repository-intelligence/coverage'


class CollectionCoverageTests(unittest.TestCase):
    def fixture(self, name):
        return load_json(FIXTURES / f'{name}.json')

    def snapshot(self, name):
        return build_repository_snapshot(self.fixture(name))

    def test_hygiene_coverage_fixture_copies_match_exact_lock(self):
        lock = load_json(ROOT / 'contracts/hygiene.repository-intelligence.alpha2.lock.json')
        self.assertEqual('1.0.0-alpha.2', lock['upstream_contract_version'])
        self.assertRegex(lock['upstream_revision'], r'^[0-9a-f]{40}$')
        for artifact in lock['coverage_fixtures']:
            path = FIXTURES / Path(artifact['path']).name
            self.assertEqual(artifact['sha256'], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_roadmap_only_leaves_every_other_domain_uncollected(self):
        projection = self.fixture('roadmap-only')
        snapshot = build_repository_snapshot(projection)
        self.assertEqual('observed', snapshot['coverage']['domains']['roadmap']['collection'])
        for domain in set(COLLECTION_DOMAINS) - {'roadmap'}:
            self.assertEqual('uncollected', snapshot['coverage']['domains'][domain]['collection'])
        self.assertEqual([], snapshot['views']['journey']['events'])
        self.assertEqual('uncollected', extract_view(snapshot, 'journey')['data']['collection_coverage']['history']['collection'])
        self.assertEqual([], snapshot['views']['decisions']['decisions'])
        self.assertEqual([], snapshot['views']['health']['checks'])
        self.assertEqual([], snapshot['views']['releases']['releases'])
        self.assertEqual([], snapshot['views']['work']['open_issues'])
        self.assertFalse(any(e['kind'] == 'issue' for e in snapshot['graph']['entities']))
        expected = next(e for e in projection['entities'] if e['kind'] == 'roadmap_step')
        step = next(s for s in snapshot['views']['roadmap']['steps'] if s['entity']['id'] == expected['id'])
        self.assertEqual(expected['state']['value'], step['entity']['state'])
        self.assertEqual(expected['attributes']['issue_references'], step['issue_references'])
        self.assertEqual([], step['tracked_by'])

    def test_zero_open_issues_is_not_a_collection_claim(self):
        states = {'roadmap-only':'uncollected', 'provider-denied':'unavailable',
                  'partial':'partial', 'failed':'failed', 'observed-empty':'observed_empty',
                  'full':'observed', 'stale':'observed'}
        for name, state in states.items():
            with self.subTest(name=name):
                snapshot = self.snapshot(name)
                work = extract_view(snapshot, 'work')['data']
                # The full fixture has a closed issue, so all these views look empty.
                self.assertEqual([], work['open_issues'])
                self.assertEqual(state, work['collection_coverage']['issues']['collection'])
        self.assertEqual('stale', self.snapshot('stale')['coverage']['domains']['issues']['freshness'])

    def test_record_freshness_and_conformance_do_not_imply_complete_collection(self):
        snapshot = self.snapshot('roadmap-only')
        self.assertEqual('current', snapshot['coverage']['record_status'])
        self.assertEqual('unknown', snapshot['coverage']['domains']['checks']['freshness'])
        self.assertIsNone(snapshot['views']['health']['score'])
        self.assertNotIn('status', snapshot['coverage'])
        self.assertNotIn('coverage_status', snapshot['views']['now'])

    def test_explicit_not_applicable_is_preserved_without_inference(self):
        coverage = self.snapshot('not-applicable')['views']['releases']['collection_coverage']
        self.assertEqual('not_applicable', coverage['deployments']['collection'])
        self.assertEqual('explicit_not_applicable', coverage['deployments']['reason'])
        self.assertEqual('observed_empty', coverage['releases']['collection'])

    def test_legacy_complete_fixture_preserves_graph_but_claims_no_completeness(self):
        projection = load_json(ROOT / 'fixtures/repository-intelligence/relay-complete-quest.input.json')
        snapshot = build_repository_snapshot(projection)
        for collection in ('entities', 'relationships', 'sources', 'events', 'redactions'):
            self.assertEqual(projection[collection], snapshot['graph'][collection])
        for coverage in snapshot['coverage']['domains'].values():
            self.assertEqual({'collection':'unavailable', 'freshness':'unknown',
                              'reason':'legacy_unspecified', 'observed_at':None}, coverage)
        self.assertEqual('1.0.0-alpha.1', snapshot['upstream']['contract_version'])
        self.assertEqual('1.0.0-alpha.2', snapshot['contract_version'])

    def test_every_view_and_fleet_keeps_collection_claims_with_repository_context(self):
        partial = self.snapshot('roadmap-only')
        legacy = build_repository_snapshot(load_json(ROOT / 'fixtures/repository-intelligence/observatory-active.input.json'))
        fleet = build_fleet_snapshot([partial, legacy])
        self.assertEqual(fleet, build_fleet_snapshot([legacy, partial]))
        self.assertEqual(partial['coverage'], fleet['repositories'][1]['coverage'])
        for view in VIEW_NAMES:
            data = extract_view(fleet, view)['data']
            if view == 'search':
                claims = next(r['domains'] for r in data['collection_coverage'] if r['repository']=='egohygiene/relay')
            else:
                claims = next(r['data']['collection_coverage'] for r in data['repositories'] if r['repository']=='egohygiene/relay')
            self.assertEqual(partial['views'][view]['collection_coverage'], claims)
        self.assertEqual('public', extract_view(fleet, 'work')['visibility'])

    def test_collection_order_does_not_change_bytes_or_mutate_input(self):
        source = self.fixture('full'); original = deepcopy(source)
        expected = json_text(build_repository_snapshot(source))
        self.assertEqual(original, source)
        source['collection_coverage'] = dict(reversed(list(source['collection_coverage'].items())))
        for name in ('entities', 'relationships', 'events', 'sources'):
            source[name].reverse()
        self.assertEqual(expected, json_text(build_repository_snapshot(source)))

    def test_invalid_coverage_fails_without_leaking_unknown_keys_or_values(self):
        for value in (None, {}, [], True, 42, 'protected/hidden'):
            candidate = self.fixture('full'); candidate['collection_coverage'] = value
            with self.assertRaises(ContractError): build_repository_snapshot(candidate)
            for key in ('collection', 'freshness', 'reason', 'observed_at'):
                candidate = self.fixture('full'); candidate['collection_coverage']['issues'][key] = value
                with self.assertRaises(ContractError) as error: build_repository_snapshot(candidate)
                self.assertNotIn('protected/hidden', str(error.exception))
        for key in ('repository','count','url','message','extensions'):
            candidate = self.fixture('provider-denied')
            candidate['collection_coverage']['issues'][key] = 'protected/hidden'
            with self.assertRaises(ContractError) as error: build_repository_snapshot(candidate)
            self.assertNotIn('protected/hidden', str(error.exception))

    def test_false_empty_missing_domains_and_incompatible_versions_fail_closed(self):
        for domain in COLLECTION_DOMAINS:
            candidate = self.fixture('full'); del candidate['collection_coverage'][domain]
            with self.assertRaises(ContractError): build_repository_snapshot(candidate)
        for version in ('1.0.0-alpha.1', '1.0.0-alpha.3', '1.0.0'):
            candidate = self.fixture('full'); candidate['contract_version'] = version
            with self.assertRaises(ContractError): build_repository_snapshot(candidate)
        for state in ('observed_empty','uncollected','unavailable','failed','not_applicable'):
            candidate = self.fixture('full'); candidate['collection_coverage']['issues']['collection'] = state
            with self.assertRaises(ContractError): build_repository_snapshot(candidate)
        candidate = self.fixture('observed-empty'); candidate['collection_coverage']['issues']['collection'] = 'observed'
        with self.assertRaises(ContractError): build_repository_snapshot(candidate)

    def test_filtering_truncation_and_observation_time_cannot_claim_current_zero(self):
        for reason in ('filtered','truncated','incomplete'):
            candidate = self.fixture('partial'); candidate['collection_coverage']['issues']['reason'] = reason
            self.assertEqual('partial', build_repository_snapshot(candidate)['coverage']['domains']['issues']['collection'])
            candidate['collection_coverage']['issues']['collection'] = 'observed_empty'
            with self.assertRaises(ContractError): build_repository_snapshot(candidate)
        for value in ('2099-01-01T00:00:00Z', '2026-02-30T00:00:00Z','2026-08-26', 'protected/hidden'):
            candidate = self.fixture('full'); candidate['collection_coverage']['issues']['observed_at'] = value
            with self.assertRaises(ContractError): build_repository_snapshot(candidate)

    def test_snapshot_consumers_reject_old_versions_instead_of_relabeling_them(self):
        snapshot = self.snapshot('full'); old = deepcopy(snapshot)
        old['contract_version'] = '1.0.0-alpha.1'
        for action in (lambda: extract_view(old, 'work'), lambda: build_fleet_snapshot([old]),
                       lambda: compare_snapshots(old, snapshot)):
            with self.assertRaisesRegex(ContractError, 'unsupported snapshot contract version'): action()

    def test_saved_views_cannot_drop_or_upgrade_collection_claims(self):
        for fleet in (False, True):
            snapshot = self.snapshot('provider-denied')
            if fleet:
                snapshot = build_fleet_snapshot([snapshot])
                payload = snapshot['views']['work']['repositories'][0]['data']
            else:
                payload = snapshot['views']['work']
            payload['collection_coverage']['issues']['collection'] = 'observed_empty'
            with self.assertRaises(ContractError): extract_view(snapshot, 'work')
        snapshot = self.snapshot('full')
        del snapshot['coverage']['domains']
        with self.assertRaises(ContractError): extract_view(snapshot, 'work')
        fleet = build_fleet_snapshot([self.snapshot('full')])
        fleet['views']['search']['collection_coverage'] = []
        with self.assertRaises(ContractError): extract_view(fleet, 'search')

    def test_fleet_does_not_mix_public_and_protected_snapshots(self):
        public = self.snapshot('full')
        private = build_repository_snapshot(load_json(ROOT / 'fixtures/repository-intelligence/observatory-active.input.json'))
        private['visibility'] = 'private'
        with self.assertRaisesRegex(ContractError, 'same visibility') as error:
            build_fleet_snapshot([public, private])
        self.assertNotIn('observatory', str(error.exception))

    def test_denied_cli_input_emits_no_artifact_or_sensitive_diagnostic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / 'input.json'; output = root / 'output'
            candidate = self.fixture('provider-denied')
            candidate['collection_coverage']['protected/hidden'] = {'count': 971}
            source.write_text(json.dumps(candidate))
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = main(['build','--input',str(source),'--output',str(output)])
            self.assertEqual(2, result)
            self.assertFalse(output.exists())
            for sensitive in ('protected/hidden','971'):
                self.assertNotIn(sensitive, stdout.getvalue()+stderr.getvalue())

    def test_all_new_goldens_are_exact_and_match_output_schemas(self):
        schemas = {name: load_json(ROOT / 'schemas' / f'repository-intelligence-{name}.v1.schema.json')
                   for name in ('read-model','view','fleet','compare')}
        validators = {}
        for name, schema in schemas.items():
            Draft202012Validator.check_schema(schema)
            validators[name] = Draft202012Validator(schema, format_checker=FormatChecker())
        for path in sorted(FIXTURES.glob('*.json')):
            snapshot = build_repository_snapshot(load_json(path))
            self.assertEqual((ROOT/'fixtures/expected/coverage'/f'{path.stem}.repository.json').read_text(), json_text(snapshot))
            validators['read-model'].validate(snapshot)
            for name in VIEW_NAMES:
                validators['view'].validate(extract_view(snapshot,name))
            fleet = build_fleet_snapshot([snapshot])
            validators['fleet'].validate(fleet)
            for name in VIEW_NAMES:
                validators['view'].validate(extract_view(fleet,name))
            validators['compare'].validate(compare_snapshots(snapshot,snapshot))
        old = self.snapshot('full'); old['contract_version'] = '1.0.0-alpha.1'
        self.assertTrue(list(validators['read-model'].iter_errors(old)))
        missing = self.snapshot('full'); del missing['views']['journey']['collection_coverage']
        self.assertTrue(list(validators['read-model'].iter_errors(missing)))


if __name__ == '__main__':
    unittest.main()
