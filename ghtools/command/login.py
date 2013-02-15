from __future__ import print_function

from getpass import getpass, _raw_input
import logging
import sys

from argh import ArghParser, arg
from ghtools import cli
from ghtools.api import envkey, GithubAPIClient

log = logging.getLogger(__name__)
parser = ArghParser()


def login_if_needed(gh, scopes, comment):
    if gh.logged_in:
        log.info("Already logged in")
        return

    print("Please log into GitHub ({0})".format(gh.nickname or "public"),
          file=sys.stderr)
    username = _raw_input("Username: ")
    password = getpass("Password: ")

    gh.login(username, password, scopes=scopes, comment=comment)


@arg('-s', '--scope',
     default=None,
     action='append',
     help='GitHub auth scopes to request')
@arg('-c', '--comment',
     help='Comment to attach to the auth token request')
@arg('github',
     nargs='?',
     help='GitHub instance nickname (e.g "enterprise")')
def login(args):
    """
    Log into a GitHub instance, and print the resulting OAuth token.
    """
    with cli.catch_api_errors():
        client = GithubAPIClient(nickname=args.github)
        login_if_needed(client, args.scope, comment=args.comment)

        oauth_token_key = envkey(client.nickname, 'oauth_token')
        print("export {0}='{1}'".format(oauth_token_key, client.token))
parser.set_default_command(login)


def main():
    parser.dispatch()

if __name__ == '__main__':
    main()
