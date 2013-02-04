import logging
import os
import tempfile
import shutil
from subprocess import call

log = logging.getLogger(__name__)


def migrate(src, dst, repo):
    if not src.get_project(repo).json['has_wiki']:
        log.info("Migrating repo %s -> wiki (skipping)", repo)
        return

    dst.client.patch('/repos/{0}'.format(dst.full_name(repo)), data={'has_wiki': 'true'})

    checkout = tempfile.mkdtemp()
    try:
        _migrate(src, dst, repo, checkout)
    finally:
        shutil.rmtree(checkout)


def _migrate(src, dst, repo, checkout):
    log.info("Migrating repo %s -> wiki", repo)

    src_url = src.wiki_url(repo)
    log.info("Migrating repo %s -> wiki -> cloning from %s", repo, src_url)
    call(['git', 'clone', '--mirror', src_url, checkout])

    os.chdir(checkout)

    dst_url = dst.wiki_url(repo)
    log.info("Migrating repo %s -> wiki -> pushing to %s", repo, dst_url)
    call(['git', 'remote', 'add', 'dest', dst_url])
    call(['git', 'push', '--mirror', 'dest'])
