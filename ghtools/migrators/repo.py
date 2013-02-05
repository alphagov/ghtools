import logging
import os
import tempfile
import shutil
from subprocess import call

log = logging.getLogger(__name__)


def migrate(src, dst):
    checkout = tempfile.mkdtemp()
    try:
        _migrate(src, dst, checkout)
    finally:
        shutil.rmtree(checkout)


def _migrate(src, dst, checkout):
    log.info("Migrating %s to %s -> git data", src, dst)

    log.debug("Migrating %s to %s -> git data -> cloning from %s", src, dst, src.git_url)
    call(['git', 'clone', '--mirror', src.git_url, checkout])

    os.chdir(checkout)

    log.debug("Migrating %s to %s -> git data -> pushing to %s", src, dst, dst.git_url)
    call(['git', 'remote', 'add', 'dest', dst.git_url])
    call(['git', 'push', '--mirror', 'dest'])
