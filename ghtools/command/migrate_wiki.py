from __future__ import print_function

from argh import *
from ghtools.api import GithubOrganisation
from ghtools import migrators


@arg('src', help='Migration source')
@arg('dst', help='Migration destination')
@arg('project', help='Project to be migrated')
def migrate_wiki(args):
    """
    Migrate a Github wiki from one Github instance to another.

    WARNING: This will copy the git repository verbatim. Any commits on the target repository
    that are not also on the source will be lost.
    """
    src = GithubOrganisation.create(args.src)
    dst = GithubOrganisation.create(args.dst)

    migrators.wiki.migrate(src, dst, args.project)


def main():
    dispatch_command(migrate_wiki)


if __name__ == '__main__':
    main()
