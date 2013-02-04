from datetime import datetime
from os import environ as env
import json
import logging
import urlparse
import requests

from ghtools import __version__

log = logging.getLogger(__name__)

DEFAULT_GITHUB = 'public'

KNOWN_GITHUBS = {
    'public': 'https://api.github.com'
}


class GithubError(Exception):
    pass


class GithubAPIError(GithubError):
    pass


class GithubAPIClient(object):
    def __init__(self, root=None, nickname=None):
        self._session = requests.Session()
        self._session.headers['content-type'] = 'application/json'

        if nickname is not None:
            self.nickname = nickname
        else:
            self.nickname = DEFAULT_GITHUB
        self.token = self._env('oauth_token')

        # Try to ascertain GitHub API root
        if root is not None:
            self.root = root
        elif self._env('api_root') is not None:
            self.root = self._env('api_root')
        else:
            try:
                self.root = KNOWN_GITHUBS[self.nickname]
            except KeyError:
                msg = "No known API root for nickname '{0}'. Perhaps you need to set ${1}?".format(
                    self.nickname,
                    envkey(self.nickname, 'api_root')
                )
                raise GithubError(msg)

        # Use specified SSL CA Bundle if provided
        ca_bundle = self._env('ca_bundle')
        if ca_bundle is not None:
            self._session.verify = ca_bundle

        log.debug("Created %s", self)

    def _env(self, key, default=None):
        return env.get(
            envkey(self.nickname, key),
            default
        )

    def _req(self, method, url, _raise=True, *args, **kwargs):
        if "data" in kwargs and (isinstance(kwargs['data'], int) or isinstance(kwargs['data'], dict)):
            kwargs['data'] = json.dumps(kwargs['data'])

        if env.get("GHTOOLS_DEBUG", False):
            print(method, url, args, kwargs)
        res = self._session.request(method, url, *args, **kwargs)
        if env.get("GHTOOLS_DEBUG", False):
            print(res, res.text, res.headers)
        if _raise:
            custom_raise_for_status(res)
        return res

    def _url(self, path):
        return self.root + path

    def login(self, username, password, scopes=None):
        if scopes is None:
            scopes = []

        ver = __version__
        now = datetime.utcnow().replace(microsecond=0)

        note = 'ghtools {0} (created {1})'.format(ver, now.isoformat())

        data = {
            'note': note,
            'scopes': scopes,
        }

        res = self.post(
            '/authorizations',
            auth=(username, password),
            data=json.dumps(data)
        )

        self.token = res.json['token']

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, tok):
        self._token = tok
        if tok is not None:
            self._session.headers['Authorization'] = 'token {0}'.format(self._token)

    @property
    def logged_in(self):
        return self.token is not None

    def request(self, method, url, *args, **kwargs):
        return self._req(method, self._url(url), *args, **kwargs)

    def delete(self, url, *args, **kwargs):
        return self._req('delete', self._url(url), *args, **kwargs)

    def get(self, url, *args, **kwargs):
        return self._req('get', self._url(url), *args, **kwargs)

    def patch(self, url, *args, **kwargs):
        return self._req('patch', self._url(url), *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self._req('post', self._url(url), *args, **kwargs)

    def put(self, url, *args, **kwargs):
        return self._req('put', self._url(url), *args, **kwargs)

    def paged_get(self, url, *args, **kwargs):
        for res in paged(self._session, 'get', self._url(url)):
            for repo in res.json:
                yield repo

    def __str__(self):
        return '<GithubAPIClient {0}={1}>'.format(self.nickname, self.root)


def envkey(nickname, key):
    return 'GITHUB_{0}_{1}'.format(nickname.upper(), key.upper())


def paged(session, method, url, **kwargs):
    res = session.request(method, url, **kwargs)

    custom_raise_for_status(res)

    while True:
        yield res
        try:
            next_page = res.links['next']
        except KeyError:
            break
        else:
            res = session.request(method, next_page['url'], **kwargs)
            custom_raise_for_status(res)


def custom_raise_for_status(res):
    try:
        res.raise_for_status()
    except requests.RequestException as err:
        newerr = GithubAPIError(err)
        for k, v in err.__dict__.items():
            setattr(newerr, k, v)
        raise newerr


class GithubOrganisation(object):
    @classmethod
    def create(cls, path):
        nickname, organisation = path.split(':', 2)

        return GithubOrganisation(nickname, organisation, GithubAPIClient(nickname=nickname))

    def __init__(self, nickname, organisation, client):
        self.nickname = nickname
        self.organisation = organisation
        self.client = client

    @property
    def hostname(self):
        return urlparse.urlparse(self.client.root).netloc.split(":")[0]

    def full_name(self, name):
        return '{0}/{1}'.format(self.organisation, name)

    def close_issue(self, repo, issue):
        url = '/repos/{0}/issues/{1}'.format(self.full_name(repo), issue['number'])
        self.client.patch(url, data={'state': 'closed'})

    def open_issue(self, repo, issue):
        url = '/repos/{0}/issues/{1}'.format(self.full_name(repo), issue['number'])
        self.client.patch(url, data={'state': 'open'})

    def create_issue(self, repo, issue):
        url = '/repos/{0}/issues'.format(self.full_name(repo))
        self.client.post(url, data=issue)

    def create_issue_comment(self, repo, issue, comment):
        url = '/repos/{0}/issues/{1}/comments'.format(self.full_name(repo), issue['number'])
        return self.client.post(url, data=comment)

    def create_pull(self, repo, pull):
        url = '/repos/{0}/pulls'.format(self.full_name(repo))
        self.client.post(url, data=pull)

    def list_issues(self, name):
        return sorted(self._list_all_things(name, 'issues'), key=lambda i: i['number'])

    def list_issue_comments(self, name, issue):
        url = '/repos/{0}/issues/{1}/comments'.format(self.full_name(name), issue['number'])
        return self.client.paged_get(url)

    def list_pulls(self, name):
        return sorted(self._list_all_things(name, 'pulls'), key=lambda i: i['number'])

    def _list_things(self, project, type, state):
        return list(self.client.paged_get('/repos/{0}/{1}?direction=asc&state={2}'.format(self.full_name(project), type, state)))

    def _list_all_things(self, project, type):
        return self._list_things(project, type, 'closed') + self._list_things(project, type, 'open')

    def get_project(self, name):
        return self.client.get('/repos/{0}'.format(self.full_name(name)))

    def create_project(self, project):
        try:
            self.get_project(project["name"])
        except GithubAPIError as e:
            if e.response.status_code != 404:
                raise

            keys = [
                'name',
                'description',
                'homepage',
                'private',
                'has_issues',
                'has_wiki',
                'has_downloads'
            ]
            payload = dict((k, project[k]) for k in keys)
            self.client.post('/orgs/{0}/repos'.format(self.organisation), data=json.dumps(payload))
            log.info("Created %s on %s", self.full_name(project["name"]), self.client)
        else:
            log.debug("%s already exists on %s, skipping...", self.full_name(project["name"]), self.client)

    def add_public_key(self, title, key):
        self.client.post("/user/keys", data=json.dumps({
            "title": title,
            "key": key
        }))

    def remove_public_key(self, to_remove):
        for key in self.client.get("/user/keys").json:
            if key["key"] == to_remove:
                self.client.delete("/user/keys/{0}".format(key["id"]))
                return True

        return False

    def __str__(self):
        return '<GithubOrganisation {0}, {1}>'.format(self.nickname, self.organisation)
