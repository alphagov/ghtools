from ghtools.identifier import Identifier
from ghtools.util import make_client


class Organisation(object):

    def __init__(self, org, client=None):
        self._ident = Identifier.from_string(org)
        self.org = self._ident.org
        self.client = client or make_client(self._ident)

    def get_repo(self, repo):
        url = '/repos/{0}/{1}'.format(self.org, repo)
        res = self.client.get(url)
        return res.json

    def create_repo(self, repo):
        keys = [
            'name',
            'description',
            'homepage',
            'private',
            'has_issues',
            'has_wiki',
            'has_downloads'
        ]
        payload = dict((k, repo[k]) for k in keys)
        res = self.client.post('/orgs/{0}/repos'.format(self.org), data=payload)
        return res.json

    def __str__(self):
        return '<Organisation {0}>'.format(self._ident)
