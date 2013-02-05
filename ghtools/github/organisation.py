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

    def list_teams(self):
        return self.client.paged_get('/orgs/{0}/teams'.format(self.org))

    def list_team_members(self, team):
        return self.client.paged_get('/teams/{0}/members'.format(team['id']))

    def list_team_repos(self, team):
        return self.client.paged_get('/teams/{0}/repos'.format(team['id']))

    def create_team(self, team):
        return self.client.post('/orgs/{0}/teams'.format(self.org), data=team)

    def add_team_member(self, team_id, login):
        return self.client.put('/teams/{0}/members/{1}'.format(team_id, login), data=' ')

    def add_team_repo(self, team_id, repo_name):
        return self.client.put('/teams/{0}/repos/{1}'.format(team_id, repo_name), data=' ')

    def __str__(self):
        return '<Organisation {0}>'.format(self._ident)
