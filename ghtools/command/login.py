from __future__ import print_function

from getpass import getpass, _raw_input
import logging
import sys

from argh import *
from ghtools.api import GithubAPIClient, envkey

log = logging.getLogger(__name__)
parser = ArghParser()

def login_if_needed(gh, scopes):
    if gh.logged_in:
        log.info("Already logged in")
        return

    print("Please log into GitHub ({0})".format(gh.nickname or "public"), file=sys.stderr)
    username = _raw_input("Username: ")
    password = getpass("Password: ")

    gh.login(username, password, scopes=scopes)

@arg('-n', '--nickname', default='public', help='GitHub instance nickname')
@arg('-s', '--scope', default=None, action='append', help='GitHub auth scopes to request')
def login(args):
    """
    Log into a GitHub instance, and print the resulting OAuth token.
    """
    c = GithubAPIClient(nickname=args.nickname)

    login_if_needed(c, args.scope)

    print("export {0}='{1}'".format(envkey(c.nickname, 'oauth_token'), c.token))

def main():
    dispatch_command(login)

if __name__ == '__main__':
    main()
