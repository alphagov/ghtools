from __future__ import print_function

import json
import logging

from argh import ArghParser
from ghtools import cli

log = logging.getLogger(__name__)
parser = ArghParser(description="Interact with GitHub repos")
parser.add_argument('repo', help='Repo identifier, e.g. defunkt/resque, enterprise:mycorp/myproj')


def delete(args):
    """
    Delete the specified repository
    """
    ident = cli.parse_identifier(args.repo)
    c = cli.get_client(ident.github)

    with cli.catch_api_errors():
        c.delete('/repos/{0}/{1}'.format(ident.org, ident.repo))
parser.add_commands([delete])


def get(args):
    """
    Print the JSON representation of the specified repository to STDOUT
    """
    ident = cli.parse_identifier(args.repo)
    c = cli.get_client(ident.github)

    with cli.catch_api_errors():
        res = c.get('/repos/{0}/{1}'.format(ident.org, ident.repo))
        return json.dumps(res.json, indent=2)
parser.add_commands([get])


def main():
    parser.dispatch()

if __name__ == '__main__':
    main()
