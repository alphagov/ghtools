from mock import MagicMock
import json

from ..helpers import *

from ghtools.api import GithubAPIClient, GithubOrganisation, envkey, GithubAPIError

# This environment variable is expected to be set when testing. Tox will set
# it (see tox.ini)
API_ROOT = os.environ.get('GITHUB_TEST_API_ROOT')

class TestGithubAPIClient(RequestMockTestCase):

    def setup(self):
        self.session_to_patch = 'ghtools.api.requests.Session'
        super(TestGithubAPIClient, self).setup()

        self.login()

    def login(self):
        authz_resp = fixture('authz_1.json')
        self.register_response('post', API_ROOT + '/authorizations', 201, {}, authz_resp)
        self.register_response('get', API_ROOT + '/authorizations/1', 200, {}, authz_resp)

    def logout(self):
        self.register_response('get', API_ROOT + '/authorizations', 404)

    def test_login_should_set_token(self):
        c = GithubAPIClient(nickname='test')
        assert_equal(c.token, None)
        c.login('foo', 'bar')
        assert_equal(c.token, 'abc123')
        assert_true(c.logged_in)

    def test_get(self):
        self.register_response('get', API_ROOT + '/foo', 200, {}, 'foo')
        c = GithubAPIClient(nickname='test')
        assert_equal(c.get('/foo').content, 'foo')

    def test_post(self):
        self.register_response('post', API_ROOT + '/bar', 201, {}, 'bar')
        c = GithubAPIClient(nickname='test')
        assert_equal(c.post('/bar').status_code, 201)

    def test_put(self):
        self.register_response('put', API_ROOT + '/baz', 200, {}, '{"message": "success"}')
        c = GithubAPIClient(nickname='test')
        assert_equal(c.put('/baz').json, {'message': 'success'})

    def test_delete(self):
        self.register_response('delete', API_ROOT + '/bat', 204, {}, '')
        c = GithubAPIClient(nickname='test')
        assert_equal(c.delete('/bat').status_code, 204)

class TestGithubOrganisation(object):
    def setup(self):
        self.client = MagicMock(GithubAPIClient(nickname='test'))
        self.org = GithubOrganisation("test", "myorganisation", self.client)

    def teardown(self):
        del self.org, self.client

    def test_create(self):
        self.org = GithubOrganisation.create("test:myorganisation")
        assert_equal(self.org.nickname, "test")
        assert_equal(self.org.organisation, "myorganisation")
        assert_true(isinstance(self.org.client, GithubAPIClient))
        assert_equal(self.org.client.nickname, "test")

    def test_full_name(self):
        assert_equal(self.org.full_name("myproject"), "myorganisation/myproject")

    def test_get_project(self):
        self.client.get.return_value = "project data"

        assert_equal(self.org.get_project("myproject"), "project data")

        self.client.get.assert_called_with('/repos/myorganisation/myproject')

    def test_create_project_when_project_does_not_exist(self):
        error = GithubAPIError()
        error.response = MagicMock()
        error.response.status_code = 404
        self.client.get.side_effect = error
        
        project = json.loads(fixture("release_app.json"))
        self.org.create_project(project)

        payload = {
            "name": "release",
            "description": "An application to make managing releases to specific environments easier",
            "homepage": None,
            "private": False,
            "has_issues": True,
            "has_wiki": True,
            "has_downloads": True
        }
        self.client.post.assert_called_with('/orgs/myorganisation/repos', data=json.dumps(payload))

    def test_create_project_when_project_does_exist(self):
        self.client.get.return_value = "the project"

        project = json.loads(fixture("release_app.json"))
        self.org.create_project(project)

        assert_false(self.client.post.called)

    def test_create_project_error_is_not_404(self):
        error = GithubAPIError()
        error.response = MagicMock()
        error.response.status_code = 401
        self.client.get.side_effect = error

        project = json.loads(fixture("release_app.json"))
        assert_raises(GithubAPIError, self.org.create_project, project)

    def test_hostname(self):
        self.client.root = "https://imaginary.host:1234/foo/bar"

        assert_equal(self.org.hostname, "imaginary.host")

    def test_add_public_key(self):
        self.org.add_public_key("ghtools migrator", "blahblahblah")

        payload = {
            "title": "ghtools migrator",
            "key": "blahblahblah"
        }
        self.client.post.assert_called_with("/user/keys", data=json.dumps(payload))

    def test_remove_public_key(self):
        # todo: fix
        self.org.remove_public_key("blahblahblah")

        self.client.get.return_value = ""

def test_envkey():
    assert_equal(envkey('foo', 'bar'), 'GITHUB_FOO_BAR')
    assert_equal(envkey('foo', 'baz_bat'), 'GITHUB_FOO_BAZ_BAT')
