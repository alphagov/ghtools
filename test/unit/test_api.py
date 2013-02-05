from ..helpers import *

from ghtools.api import GithubAPIClient, envkey

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


def test_envkey():
    assert_equal(envkey('foo', 'bar'), 'GITHUB_FOO_BAR')
    assert_equal(envkey('foo', 'baz_bat'), 'GITHUB_FOO_BAZ_BAT')
