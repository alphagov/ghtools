import logging
from argh import arg, dispatch_command

from ghtools import cli
from ghtools.github import Organisation
from ghtools.migrators import teams

log = logging.getLogger(__name__)


@arg('src', help='Migration source')
@arg('dst', help='Migration destination')
@arg('mapping', help='Mapping file for user accounts from src to dst')
def migrate_teams(args):
    with cli.catch_api_errors():
        src = Organisation(args.src)
        dst = Organisation(args.dst)

        teams.migrate(src, dst, args.mapping)


def main():
    dispatch_command(migrate_teams)


if __name__ == '__main__':
    main()
