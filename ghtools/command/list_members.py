from __future__ import print_function
import json

from argh import *
from ghtools.api import GithubOrganisation
from collections import defaultdict
import csv
import sys

@arg('org', help='The organisation in question')
@arg('-t', '--teams', default=False, help='Add member teams')
def list_members(args):
	"""
	List all members of an organisation along with the teams they're in.
	"""

	org = GithubOrganisation.create(args.org)

	members = defaultdict(list)
	for team in org.client.paged_get('/orgs/{0}/teams'.format(org.organisation)):
		for member in org.client.paged_get('/teams/{0}/members'.format(team['id'])):
			members[member["login"]].append(team["name"])

	writer = csv.writer(sys.stdout, delimiter=',', quotechar='"')

	for member in org.client.paged_get('/orgs/{0}/members'.format(org.organisation)):
		if member["type"] == "User":
			writer.writerow([member['login']] + members[member['login']])

def main():
	dispatch_command(list_members)

if __name__ == '__main__':
	main()