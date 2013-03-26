import itertools
import logging

from ghtools.exceptions import GithubError
from ghtools.identifier import Identifier
from ghtools.util import make_client

log = logging.getLogger(__name__)


class Repo(object):

    def __init__(self, repo, client=None):
        self._ident = Identifier.from_string(repo)

        if self._ident.repo is None:
            raise GithubError("Invalid repo string '{0}'".format(repo))

        self.org = self._ident.org
        self.repo = self._ident.repo
        self.client = client or make_client(self._ident)

    @property
    def ssh_url(self):
        res = self.client.get('/repos/{0}'.format(self.org_repo))
        return res.json()['ssh_url']

    @property
    def wiki_ssh_url(self):
        ssh_url = self.ssh_url
        if not ssh_url.endswith('.git'):
            raise GithubError("ssh_url doesn't end with '.git', bailing!")
        return ssh_url[:-len('.git')] + '.wiki.git'

    @property
    def org_repo(self):
        return '{0}/{1}'.format(self.org, self.repo)

    def create_commit_comment(self, commit_id, comment):
        url = '/repos/{0}/commits/{1}/comments'.format(self.org_repo, commit_id)
        res = self.client.post(url, data=comment)
        return res.json()

    def create_hook(self, hook):
        url = '/repos/{0}/hooks'.format(self.org_repo)
        res = self.client.post(url, data=hook)
        return res.json()

    def create_issue(self, issue):
        url = '/repos/{0}/issues'.format(self.org_repo)
        res = self.client.post(url, data=issue)
        return res.json()

    def create_issue_comment(self, issue, comment):
        url = '/repos/{0}/issues/{1}/comments'.format(self.org_repo, issue['number'])
        res = self.client.post(url, data=comment)
        return res.json()

    def create_pull(self, pull):
        url = '/repos/{0}/pulls'.format(self.org_repo)
        res = self.client.post(url, data=pull)
        return res.json()

    def delete(self):
        res = self.client.delete('/repos/{0}'.format(self.org_repo))
        return res.json()

    def get(self):
        res = self.client.get('/repos/{0}'.format(self.org_repo))
        return res.json()

    def create(self):
        repo_information = {'name': self.repo}
        res = self.client.post('/orgs/{0}/repos'.format(self.org), data=repo_information)
        return res.json()

    def list_commit_comments(self):
        url = '/repos/{0}/comments'.format(self.org_repo)
        return self.client.paged_get(url.format(self.org_repo, 'open'))

    def list_commits(self):
        url = '/repos/{0}/commits'.format(self.org_repo)
        return self.client.paged_get(url.format(self.org_repo))

    def list_hooks(self):
        url = '/repos/{0}/hooks'.format(self.org_repo)
        return self.client.paged_get(url.format(self.org_repo, 'open'))

    def list_issues(self, include_closed=False):
        url = '/repos/{0}/issues?direction=asc&state={1}'
        open_issues = self.client.paged_get(url.format(self.org_repo, 'open'))

        if include_closed:
            closed_issues = self.client.paged_get(url.format(self.org_repo, 'closed'))
            return itertools.chain(open_issues, closed_issues)
        else:
            return open_issues

    def list_issue_comments(self, issue):
        url = '/repos/{0}/issues/{1}/comments'.format(self.org_repo, issue['number'])
        return self.client.paged_get(url)

    def list_pulls(self, include_closed=False):
        url = '/repos/{0}/pulls?direction=asc&state={1}'
        open_pulls = self.client.paged_get(url.format(self.org_repo, 'open'))

        if include_closed:
            closed_pulls = self.client.paged_get(url.format(self.org_repo, 'closed'))
            return itertools.chain(open_pulls, closed_pulls)
        else:
            return open_pulls

    def close_issue(self, issue):
        url = '/repos/{0}/issues/{1}'.format(self.org_repo, issue['number'])
        res = self.client.patch(url, data={'state': 'closed'})
        return res.json()

    def open_issue(self, issue):
        url = '/repos/{0}/issues/{1}'.format(self.org_repo, issue['number'])
        res = self.client.patch(url, data={'state': 'open'})
        return res.json()

    def set_build_status(self, sha, status):
        url = '/repos/{0}/statuses/{1}'.format(self.org_repo, sha)
        return self.client.post(url, data=status)

    def __str__(self):
        return '<Repo {0}>'.format(self._ident)
