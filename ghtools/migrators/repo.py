import logging
import os
import tempfile
import shutil
from subprocess import check_call

log = logging.getLogger(__name__)


def migrate(src, dst):
    checkout = tempfile.mkdtemp()
    cwd = os.getcwd()
    try:
        _migrate(src, dst, checkout)
    finally:
        shutil.rmtree(checkout)
        os.chdir(cwd)


def _migrate(src, dst, checkout):
    log.info("Migrating %s to %s -> git data", src, dst)

    src_url = src.ssh_url
    log.debug("Migrating %s to %s -> git data -> cloning from %s", src, dst, src_url)
    check_call(['git', 'clone', '--mirror', src_url, checkout])

    os.chdir(checkout)

    dst_url = dst.ssh_url
    log.debug("Migrating %s to %s -> git data -> pushing to %s", src, dst, dst_url)
    check_call(['git', 'remote', 'add', 'dest', dst_url])
    check_call(['git', 'push', '--mirror', 'dest'])
