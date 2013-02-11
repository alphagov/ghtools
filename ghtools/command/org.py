from __future__ import print_function

import json

from argh import ArghParser, arg
from ghtools import cli
from ghtools.github.organisation import Organisation

parser = ArghParser(description="Interact with a GitHub organisation")
parser.add_argument('org',
                    help='Organisation identifier '
                         '(e.g. rails, enterprise:mycorp)')

json_arg = arg('-j', '--json',
               default=False,
               action='store_true',
               help='Print full JSON representations')


@json_arg
def repos(args):
    """
    Print a list of organisation repositories
    """
    with cli.catch_api_errors():
        org = Organisation(args.org)
        for repo in org.list_repos():
            if args.json:
                print(json.dumps(repo, indent=2))
            else:
                print(repo['name'])
parser.add_commands([repos])


@json_arg
def members(args):
    """
    Print a list of organisation members
    """
    with cli.catch_api_errors():
        org = Organisation(args.org)
        for member in org.list_members():
            if args.json:
                print(json.dumps(member, indent=2))
            else:
                print(member['login'])
parser.add_commands([members])


def permissions(args):
    """
    Print a list of teams.
    For each team, list the members, repos and the permission (pull/push/admin)
    """
    with cli.catch_api_errors():
        org = Organisation(args.org)
        result = []
        for team in org.list_teams():
            members = org.list_team_members(team)
            repos = org.list_team_repos(team)
            result.append({
                            "name": team['name'],
                            "permission": team['permission'],
                            "repos": [{ 'full_name': repo['full_name'], 'url': repo['url'] } for repo in repos],
                            "members": [{ 'login': member['login'], 'url': member['url'] } for member in members]
                        }) 
        print(json.dumps(result, indent=2))
parser.add_commands([permissions])


def main():
    parser.dispatch()

if __name__ == '__main__':
    main()
