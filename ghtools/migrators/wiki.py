import logging
import textwrap
import os
import tempfile
import shutil
from subprocess import check_call
from subprocess import CalledProcessError
from ghtools.exceptions import GithubError

log = logging.getLogger(__name__)


def migrate(src, dst):
    src_repo = src.client.get('/repos/{0}'.format(src.org_repo)).json()
    if not src_repo['has_wiki']:
        log.info("Migrating %s to %s -> wiki (skipping)", src, dst)
        return

    dst.client.patch('/repos/{0}'.format(dst.org_repo), data={'name': dst.repo, 'has_wiki': 'true'})

    checkout = tempfile.mkdtemp()
    cwd = os.getcwd()
    try:
        _migrate(src, dst, checkout)
    finally:
        shutil.rmtree(checkout)
        os.chdir(cwd)


def _migrate(src, dst, checkout):
    log.info("Migrating %s to %s -> wiki", src, dst)

    src_url = src.wiki_ssh_url
    log.debug("Migrating %s to %s -> wiki -> cloning from %s", src, dst, src_url)
    check_call(['git', 'clone', '--mirror', src_url, checkout])

    os.chdir(checkout)

    dst_url = dst.wiki_ssh_url
    log.debug("Migrating %s to %s -> wiki -> pushing to %s", src, dst, dst_url)
    check_call(['git', 'remote', 'add', 'dest', dst_url])

    try:
        check_call(['git', 'push', '--mirror', 'dest'])
    except CalledProcessError:
        message = textwrap.dedent(u"""
            The destination wiki does not exist, you will need to visit it at:
            {0}/wiki
            """.format(dst.client.get('/repos/{0}'.format(dst.org_repo)).json['html_url']))
        raise GithubError(message)

