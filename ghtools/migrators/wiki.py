import logging
import os
import tempfile
import shutil
from subprocess import call

log = logging.getLogger(__name__)


def migrate(src, dst):
    src_repo = src.client.get('/repos/{0}'.format(src.org_repo)).json
    if not src_repo['has_wiki']:
        log.info("Migrating %s to %s -> wiki (skipping)", src, dst)
        return

    dst.client.patch('/repos/{0}'.format(dst.org_repo), data={'name': dst.repo, 'has_wiki': 'true'})

    checkout = tempfile.mkdtemp()
    try:
        _migrate(src, dst, checkout)
    finally:
        shutil.rmtree(checkout)


def _migrate(src, dst, checkout):
    log.info("Migrating %s to %s -> wiki", src, dst)

    log.info("Migrating %s to %s -> wiki -> cloning from %s", src, dst, src.wiki_url)
    call(['git', 'clone', '--mirror', src.wiki_url, checkout])

    os.chdir(checkout)

    log.info("Migrating %s to %s -> wiki -> pushing to %s", src, dst, dst.wiki_url)
    call(['git', 'remote', 'add', 'dest', dst.wiki_url])
    call(['git', 'push', '--mirror', 'dest'])
