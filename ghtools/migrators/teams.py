import csv
import logging
from ghtools.exceptions import GithubAPIError

log = logging.getLogger(__name__)


class TeamMigrator(object):
    def __init__(self, src, dst, mapping_path):
        self.src = src
        self.dst = dst
        self._mapping = self._load_members_mapping(mapping_path)
        self._dst_teams = dict((t['name'], t) for t in self.dst.list_teams())

    def migrate(self):
        for team in self.src.list_teams():
            self._create_team(team)
            self._migrate_members(team)
            self._migrate_repos(team)

    def _create_team(self, team):
        if team['name'] in self._dst_teams:
            log.info('Team {0} already exists'.format(team['name']))
        else:
            team = {
                'name': team['name'],
                'permission': team['permission']
            }
            self._dst_teams[team['name']] = self.dst.create_team(team)

    def _migrate_members(self, team):
        for member in self.src.list_team_members(team):
            if member['login'] not in self._mapping:
                log.warning('Failed to migrate member to {0}, {1} is not in the mapping file'.format(team['name'], member['login']))
            else:
                try:
                    self.dst.add_team_member(self._dst_teams[team['name']], self._mapping[member['login']])
                    log.debug('User {0} added to {1}'.format(member['login'], team['name']))
                except GithubAPIError as e:
                    if e.response.status_code == 404:
                        log.warning('User not found, {0}'.format(self._mapping[member['login']]))
                    else:
                        raise

    def _migrate_repos(self, team):
        for repo in self.src.list_team_repos(team):
            try:
                self.dst.add_team_repo(self._dst_teams[team['name']], repo['name'])
            except GithubAPIError as e:
                if e.response.status_code == 404:
                    log.warning('Repo not found, {0}'.format(repo['name']))
                else:
                    raise

    def _load_members_mapping(self, mapping_path):
        members = {}
        with open(mapping_path, 'r') as f:
            reader = csv.reader(f, delimiter=',', quotechar='"')
            for row in reader:
                if len(row[1].strip()) > 0:
                    members[row[0]] = row[1]
        return members

def migrate(src, dst, mapping_path):
    TeamMigrator(src, dst, mapping_path).migrate()
