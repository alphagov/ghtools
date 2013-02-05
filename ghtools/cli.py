from __future__ import print_function

import contextlib
import logging
import sys

from ghtools.api import GithubAPIClient
from ghtools.exceptions import GithubError
from ghtools.identifier import Identifier

log = logging.getLogger(__name__)


@contextlib.contextmanager
def catch_api_errors():
    """

    Don't spew tracebacks to users -- catch API errors and display them in a
    nicer format.

    """
    try:
        yield
    except GithubError as e:
        fail(str(e))


def fail(message, exit_code=1):
    """Abort execution, showing the user a nice error message"""
    print(message)
    sys.exit(exit_code)


def get_client(nickname):
    """Try to create a GithubAPIClient for the given nickname"""
    try:
        return GithubAPIClient(nickname=nickname)
    except GithubError as e:
        fail(str(e))


def parse_identifier(identifier, require_repo=False):
    """Parse a user-supplied identifier"""
    ident = Identifier.from_string(identifier)
    if require_repo and ident.repo is None:
        fail('Invalid identifier supplied: "{0}" does not identify a repository!'.format(identifier))
    return ident


