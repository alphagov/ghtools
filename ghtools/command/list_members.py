from __future__ import print_function
import json

from argh import *
from ghtools import cli
from ghtools.github import Organisation
from collections import defaultdict
import csv
import sys


@arg('org', help='The organisation in question')
@arg('-t', '--teams', default=False, help='Add member teams')
def list_members(args):
    """
    List all members of an organisation along with the teams they're in.
    """
    with cli.catch_api_errors():
        org = Organisation(args.org)

        members = defaultdict(list)
        for team in org.list_teams():
            for member in org.list_team_members(team):
                members[member['login']].append(team['name'])

        writer = csv.writer(sys.stdout, delimiter=',', quotechar='"')

        for member in org.list_members():
            if member['type'] == 'User':
                writer.writerow([member['login']] + members[member['login']])

def main():
    dispatch_command(list_members)


if __name__ == '__main__':
    main()
