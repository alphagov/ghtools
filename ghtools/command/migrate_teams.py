import logging
from argh import *
import csv

from ghtools.api import GithubOrganisation, APIError
from ghtools import migrators

log = logging.getLogger(__name__)

@arg('src',     help='Migration source')
@arg('dst',     help='Migration destination')
@arg('members', help='Mapping file for user accounts from src to dst')
def migrate_teams(args):
	src = GithubOrganisation.create(args.src)
	dst = GithubOrganisation.create(args.dst)

	members = {}
	with open(args.members, 'r') as f:
		reader = csv.reader(f, delimiter=',', quotechar='"')
		for row in reader:
			if len(row[1].strip()) > 0:
				members[row[0]] = row[1]

	dst_teams = dict((t['name'], t['id']) for t in dst.client.get('/orgs/{0}/teams'.format(dst.organisation)).json)

	for src_team in src.client.get('/orgs/{0}/teams'.format(src.organisation)).json:
		if src_team['name'] in dst_teams:
			log.info("Team {0} alread exists.".format(src_team['name']))
		else:
			payload = {
				'name':       src_team['name'],
				'permission': src_team['permission']
			}

			dst_team = dst.client.post('/orgs/{0}/teams'.format(dst.organisation), data=payload).json
			dst_teams[src_team['name']] = dst_team['id']

		for src_member in src.client.get('/teams/{0}/members'.format(src_team['id'])).json:
			if src_member['login'] in members:
				try:
					dst.client.put('/teams/{0}/members/{1}'.format(dst_teams[src_team['name']], members[src_member['login']]), data=' ')
					log.debug("User '{0}' added to '{1}'".format(src_member['login'], src_team['name']))
				except APIError as e:
					if e.response.status_code == 404:
						log.error("User '{0}' not found.".format(members[src_member['login']]))
					else:
						raise
			else:
				log.error("Failed to migrate member '{0}' to team '{1}'".format(src_member['login'], src_team['name']))

		for src_repo in src.client.get('/teams/{0}/repos'.format(src_team['id'])).json:
			try:
				dst.client.put('/teams/{0}/repos/{1}'.format(dst_teams[src_team['name']], dst.full_name(src_repo['name'])), data=' ')
				log.debug("Project '{0}' to '{1}'".format(src_repo['name'], src_team['name']))
			except APIError as e:
				if e.response.status_code == 404:
					log.debug("Project '{0}' does not exist".format(src_repo['name']))
				else:
					raise



def lookup_member(login):
	return 'robyoung'

def main():
	try:
		dispatch_command(migrate_teams)
	except APIError as e:
		print(e.response.text)
		raise

if __name__ == '__main__':
	main()