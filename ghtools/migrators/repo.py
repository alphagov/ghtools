import logging
import os
import tempfile
import shutil
from subprocess import call

log = logging.getLogger(__name__)


def migrate(src, dst, repo):
    checkout = tempfile.mkdtemp()
    try:
        _migrate(src, dst, repo, checkout)
    finally:
        shutil.rmtree(checkout)


def _migrate(src, dst, repo, checkout):
    log.info("Migrating repo %s -> git data", repo)

    src_url = src.git_url(repo)
    log.info("Migrating repo %s -> git data -> cloning from %s", repo, src_url)
    call(['git', 'clone', '--mirror', src_url, checkout])

    os.chdir(checkout)

    dst_url = dst.git_url(repo)
    log.info("Migrating repo %s -> git data -> pushing to %s", repo, dst_url)
    call(['git', 'remote', 'add', 'dest', dst_url])
    call(['git', 'push', '--mirror', 'dest'])
