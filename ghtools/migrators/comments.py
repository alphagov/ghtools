import logging
import textwrap

from ghtools.exceptions import GithubAPIError
from ghtools.migrators.issues import _get_author

log = logging.getLogger(__name__)


def migrate(src, dst):
    log.info("Migrating %s to %s -> commit comments", src, dst)

    for comment in src.list_commit_comments():
        body = _generate_comment_body(src.client, comment)

        payload = {
            'body': body,
            'path': comment['path'],
            'position': comment['position'],
            'line': comment['line']
        }

        try:
            dst.create_commit_comment(comment['commit_id'], payload)
        except GithubAPIError as e:
            if e.response.status_code == 404:
                log.warn('Could not create comment on commit %s: %s', comment['commit_id'], payload)
                log.warn('This is probably harmless, as the commit may have been rebased out of existence.')
            else:
                raise


def _generate_comment_body(client, comment):
    comment_template = textwrap.dedent(u"""
    <a href="{author_url}">{author}</a>:
    {body}

    <em><a href="{url}">Original comment</a> created at {created_at}.</em>
    """)

    author = _get_author(client, comment['user']['login'])

    return comment_template.format(author=author['login'],
                                   author_url=author['html_url'],
                                   body=comment['body'],
                                   created_at=comment['created_at'],
                                   url=comment['html_url'])
