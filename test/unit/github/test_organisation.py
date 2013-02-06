from mock import MagicMock, patch
import json

from ...helpers import *

from ghtools.github import Organisation


class TestOrganisation(object):

    def setup(self):
        self.patcher = patch('ghtools.github.organisation.make_client')
        self.mock_client_cons = self.patcher.start()
        self.mock_client = self.mock_client_cons.return_value
        self.o = Organisation('foo')

    def teardown(self):
        self.patcher.stop()

    def test_add_team_member(self):
        self.mock_client.put.return_value.json.return_value = {'id': 456}
        res = self.o.add_team_member({'id': 123}, 'joebloggs')
        self.mock_client.put.assert_called_with('/teams/123/members/joebloggs', data=' ')
        assert_equal(res, {'id': 456})

    def test_add_team_repo(self):
        self.mock_client.put.return_value.json.return_value = {'id': 456}
        res = self.o.add_team_repo({'id': 123}, 'myproj')
        self.mock_client.put.assert_called_with('/teams/123/repos/myproj', data=' ')
        assert_equal(res, {'id': 456})

    def test_create_repo(self):
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

        self.o.create_repo(repo)
        self.mock_client.post.assert_called_with('/orgs/foo/repos', data=repo_passed)

    def test_create_team(self):
        self.mock_client.post.return_value.json.return_value = {'id': 456}
        res = self.o.create_team({'id': 123})
        self.mock_client.post.assert_called_with('/orgs/foo/teams', data={'id': 123})
        assert_equal(res, {'id': 456})

    def test_get_repo(self):
        self.o.get_repo('bar')
        self.mock_client.get.assert_called_with('/repos/foo/bar')

    def test_get_repo_nickname(self):
        o = Organisation('enterprise:foo')
        o.get_repo('bar')
        self.mock_client.get.assert_called_with('/repos/foo/bar')

    def test_list_members(self):
        self.o.list_members()
        self.mock_client.paged_get.assert_called_with('/orgs/foo/members')

    def test_list_repos(self):
        self.o.list_repos()
        self.mock_client.paged_get.assert_called_with('/orgs/foo/repos')

    def test_list_teams(self):
        self.o.list_teams()
        self.mock_client.paged_get.assert_called_with('/orgs/foo/teams')

    def test_list_team_members(self):
        self.o.list_team_members({'id': 123})
        self.mock_client.paged_get.assert_called_with('/teams/123/members')

    def test_list_team_repos(self):
        self.o.list_team_repos({'id': 123})
        self.mock_client.paged_get.assert_called_with('/teams/123/repos')

    def test_str(self):
        o1 = Organisation('foo')
        assert_equal(str(o1), '<Organisation foo>')
        o2 = Organisation('enterprise:foo')
        assert_equal(str(o2), '<Organisation enterprise:foo>')
