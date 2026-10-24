"""The ast-grep action and workflow: a pinned, checksummed tool and caller input that reaches the
shell only through the environment."""
from pathlib import Path
import re
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
ACTION = yaml.load((ROOT / 'actions/ast-grep/action.yml').read_text(), Loader=yaml.BaseLoader)
WORKFLOW = yaml.load((ROOT / '.github/workflows/ast-grep.yml').read_text(), Loader=yaml.BaseLoader)
OWN_ACTION = re.compile(r'^storytold/craft-common-actions/actions/[a-z0-9-]+@main$')


class AstGrepTests(unittest.TestCase):
    def test_inputs_reach_scripts_only_through_env(self):
        for s in ACTION['runs']['steps'] + WORKFLOW['jobs']['scan']['steps']:
            if 'run' in s:
                with self.subTest(step=s.get('name')):
                    self.assertNotIn('${{', s['run'])

    def test_third_party_actions_are_pinned_to_a_commit(self):
        for s in WORKFLOW['jobs']['scan']['steps']:
            if 'uses' in s and not OWN_ACTION.match(s['uses']):
                self.assertRegex(s['uses'], r'@[0-9a-f]{40}$')

    def test_the_default_version_has_a_checksum(self):
        version = ACTION['inputs']['version']['default']
        self.assertIn(f'"{version}") expected="', ACTION['runs']['steps'][0]['run'])
        self.assertEqual(version, WORKFLOW['on']['workflow_call']['inputs']['version']['default'])

    def test_the_workflow_passes_every_action_input(self):
        step = next(s for s in WORKFLOW['jobs']['scan']['steps'] if s.get('uses', '').endswith('/ast-grep@main'))
        self.assertEqual(set(step['with']), set(ACTION['inputs']))
        self.assertEqual(set(WORKFLOW['on']['workflow_call']['inputs']), set(ACTION['inputs']))


if __name__ == '__main__':
    unittest.main()
