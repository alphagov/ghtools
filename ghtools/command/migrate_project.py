from __future__ import print_function

from argh import *
from ghtools.api import GithubOrganisation
from ghtools import migrators


@arg('src', help='Migration source')
@arg('dst', help='Migration destination')
@arg('project', help='Project to be migrated')
def migrate_project(args):
    """
    Migrate a Github project from one Github instance to another.

    Migration includes:
        - Project metadata
        - Git repository
        - Issues & pull requests
        - Comments
        - Hooks

    WARNING: This will copy the git repository verbatim. Any commits on the target repository
    that are not also on the source will be lost.

    Note: All issues and comments will be migrated as the target user with links back to the
    source Github instance.
    """
    src = GithubOrganisation.create(args.src)
    dst = GithubOrganisation.create(args.dst)

    migrators.project.migrate(src, dst, args.project)
    migrators.repo.migrate(src, dst, args.project)
    migrators.issues.migrate(src, dst, args.project)
    migrators.comments.migrate(src, dst, args.project)
    migrators.hooks.migrate(src, dst, args.project)

def main():
    dispatch_command(migrate_project)


if __name__ == '__main__':
    main()
