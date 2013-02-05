from __future__ import print_function

from argh import *
from ghtools import cli
from ghtools.github import Repo
from ghtools import migrators

@arg('src', help='Migration source')
@arg('dst', help='Migration destination')
def migrate_wiki(args):
    """
    Migrate a Github wiki from one Github instance to another.

    WARNING: This will copy the git repository verbatim. Any commits on the target repository
    that are not also on the source will be lost.
    """
    with cli.catch_api_errors():
        src = Repo(args.src)
        dst = Repo(args.dst)

        migrators.wiki.migrate(src, dst)


def main():
    dispatch_command(migrate_wiki)


if __name__ == '__main__':
    main()
