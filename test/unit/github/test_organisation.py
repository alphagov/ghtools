from mock import MagicMock, patch
import json

from ...helpers import *

from ghtools.github import Organisation


class TestOrganisation(object):

    def setup(self):
        self.patcher = patch('ghtools.github.organisation.make_client')
        self.mock_client_cons = self.patcher.start()
        self.mock_client = self.mock_client_cons.return_value

    def teardown(self):
        self.patcher.stop()

    def test_get_repo(self):
        o = Organisation('foo')
        o.get_repo('bar')
        self.mock_client.get.assert_called_with('/repos/foo/bar')

    def test_get_repo_nickname(self):
        o = Organisation('enterprise:foo')
        o.get_repo('bar')
        self.mock_client.get.assert_called_with('/repos/foo/bar')

    def test_create_repo(self):
        o = Organisation('foo')
        repo = {
            'name': 'reponame',
            'description': 'My description',
            'homepage': 'http://google.com',
            'private': False,
            'has_issues': False,
            'has_wiki': False,
            'has_downloads': False,
            'not_included': "I shouldn't be included",
        }

        repo_passed = repo.copy()
        del repo_passed['not_included']

        o.create_repo(repo)
        self.mock_client.post.assert_called_with('/orgs/foo/repos', data=repo_passed)

    def test_str(self):
        o1 = Organisation('foo')
        assert_equal(str(o1), '<Organisation foo>')
        o2 = Organisation('enterprise:foo')
        assert_equal(str(o2), '<Organisation enterprise:foo>')
