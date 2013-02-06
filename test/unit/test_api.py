from ..helpers import *

import os

from ghtools.api import GithubAPIClient, DEFAULT_GITHUB
from ghtools.api import envkey
from ghtools.exceptions import GithubError

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

    def test_default_to_default_github(self):
        c = GithubAPIClient()
        assert_equal(c.nickname, DEFAULT_GITHUB)

    def test_explicitly_set_root(self):
        c = GithubAPIClient('https://github.mycorp/api/v3', nickname='mycorp')
        assert_equal(c.nickname, 'mycorp')
        assert_equal(c.root, 'https://github.mycorp/api/v3')

    def test_raise_if_unknown_github(self):
        with assert_raises(GithubError) as e:
            GithubAPIClient(nickname='unknown')
            assert_regexp_matches(r'No known API root', e.message)

    def test_use_specified_ca_bundle(self):
        os.environ['GITHUB_TEST_CA_BUNDLE'] = '/usr/share/openssl/bundle.pem'
        c = GithubAPIClient(nickname='test')
        assert_equal(c._session.verify, '/usr/share/openssl/bundle.pem')
        del os.environ['GITHUB_TEST_CA_BUNDLE']

    def test_login_should_set_token(self):
        c = GithubAPIClient(nickname='test')
        assert_equal(c.token, None)
        c.login('foo', 'bar')
        assert_equal(c.token, 'abc123')
        assert_true(c.logged_in)

    def test_request(self):
        self.register_response('options', API_ROOT + '/foo', 200, {}, 'foo')
        c = GithubAPIClient(nickname='test')
        assert_equal(c.request('options', '/foo').content, 'foo')

    def test_delete(self):
        self.register_response('delete', API_ROOT + '/bat', 204, {}, '')
        c = GithubAPIClient(nickname='test')
        assert_equal(c.delete('/bat').status_code, 204)

    def test_get(self):
        self.register_response('get', API_ROOT + '/foo', 200, {}, 'foo')
        c = GithubAPIClient(nickname='test')
        assert_equal(c.get('/foo').content, 'foo')

    def test_patch(self):
        self.register_response('patch', API_ROOT + '/foo', 200, {}, 'foo')
        c = GithubAPIClient(nickname='test')
        assert_equal(c.patch('/foo').content, 'foo')

    def test_post(self):
        self.register_response('post', API_ROOT + '/bar', 201, {}, 'bar')
        c = GithubAPIClient(nickname='test')
        assert_equal(c.post('/bar').status_code, 201)

    def test_put(self):
        self.register_response('put', API_ROOT + '/baz', 200, {}, '{"message": "success"}')
        c = GithubAPIClient(nickname='test')
        assert_equal(c.put('/baz').json(), {'message': 'success'})

    def test_paged_get(self):
        self.register_response('get', API_ROOT + '/paged', 200,
                               {'link': '<{0}/paged?page=2>; rel="next"'.format(API_ROOT)},
                               '[{"item": 1}, {"item": 2}]')
        self.register_response('get', API_ROOT + '/paged?page=2', 200, {}, '[{"item": 3}]')
        client = GithubAPIClient(nickname='test')
        res = client.paged_get('/paged')
        assert_equal(res.next(), {'item': 1})
        assert_equal(res.next(), {'item': 2})
        assert_equal(res.next(), {'item': 3})
        with assert_raises(StopIteration):
            res.next()


def test_envkey():
    assert_equal(envkey('foo', 'bar'), 'GITHUB_FOO_BAR')
    assert_equal(envkey('foo', 'baz_bat'), 'GITHUB_FOO_BAZ_BAT')
