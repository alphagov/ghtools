from __future__ import print_function

import json

from argh import ArghParser, arg
from ghtools import cli

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
    ident = cli.parse_identifier(args.org)
    c = cli.get_client(ident.github)
    with cli.catch_api_errors():
        for repo in c.paged_get('/orgs/{0}/repos'.format(ident.org)):
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
    ident = cli.parse_identifier(args.org)
    c = cli.get_client(ident.github)
    with cli.catch_api_errors():
        for repo in c.paged_get('/orgs/{0}/members'.format(ident.org)):
            if args.json:
                print(json.dumps(repo, indent=2))
            else:
                print(repo['login'])
parser.add_commands([members])


def main():
    parser.dispatch()

if __name__ == '__main__':
    main()
