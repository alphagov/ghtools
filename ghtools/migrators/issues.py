import logging
import textwrap

from ghtools.api import GithubAPIError

log = logging.getLogger(__name__)


class IssueMigrator(object):

    def __init__(self, src, dst, repo):
        self.src = src
        self.dst = dst
        self.repo = repo

    def migrate(self):
        log.debug("Migrating repo %s -> issues", self.repo)

        for issue in self.src.list_issues(self.repo):
            self._migrate_issue(issue)

        for pull in self.src.list_pulls(self.repo):
            self._migrate_pull(pull)

    def _migrate_issue(self, issue):
        log.debug("Migrating repo %s -> issues -> #%s", self.repo, issue['number'])

        payload = {
            'title': issue['title'],
            'body': self._generate_issue_body(issue),
            # 'assignee':  issue['assignee'], # cannot migrate until users have been migrated
            'milestone': issue['milestone'],
            'labels': [label['name'] for label in issue['labels']]
        }

        self.dst.create_issue(self.repo, payload)

        issue_comments = self.src.list_issue_comments(self.repo, issue)
        sorted_comments = sorted(issue_comments, key=lambda x: x['created_at'])

        should_close = (issue['state'] == 'closed')

        for comment in sorted_comments:
            if should_close and comment['created_at'] > issue['closed_at']:
                self.dst.close_issue(self.repo, issue)
                should_close = False

            payload = {'body': self._generate_comment_body(issue, comment)}
            self.dst.create_issue_comment(self.repo, issue, payload)

        if should_close:
            self.dst.close_issue(self.repo, issue)

    def _migrate_pull(self, pull):
        log.debug("Migrating repo %s -> issues -> PR #%s", self.repo, pull['number'])

        payload = {
            'issue': pull['number'],
            'head': pull['head']['sha'],
            'base': pull['base']['sha']
        }

        try:
            self.dst.create_pull(self.repo, payload)
        except GithubAPIError as e:
            if e.response.status_code == 500:
                log.error("Failed to migrate pull request, maybe the branch was deleted?")
            else:
                raise

    def _generate_issue_body(self, issue):
        issue_template = textwrap.dedent("""
        {body}

        <table>
        <legend><em>Details for original issue <a href="{url}">{shortname}</a>:</em></legend>
        <tr><td><strong>Author</strong></td><td><a href="{author_url}">{author}</a></td></tr>
        <tr><td><strong>Created at<strong></td><td>{created_at}</td></tr>
        </table>
        """)

        author = _get_author(self.src.client, issue['user']['login'])
        shortname = '{0}#{1}'.format(self.src.full_name(self.repo), issue['number'])

        return issue_template.format(author=author['login'],
                                     author_url=author['html_url'],
                                     body=issue['body'],
                                     created_at=issue['created_at'],
                                     url=issue['html_url'],
                                     shortname=shortname)

    def _generate_comment_body(self, issue, comment):
        comment_template = textwrap.dedent("""
        {body}

        <table>
        <legend><em>Details for <a href="{url}">original comment</a>:</em></legend>
        <tr><td><strong>Author</strong></td><td><a href="{author_url}">{author}</a></td></tr>
        <tr><td><strong>Created at<strong></td><td>{created_at}</td></tr>
        </table>
        """)

        author = _get_author(self.src.client, comment['user']['login'])
        comment_url = '{0}#issuecomment-{1}'.format(issue['html_url'], comment['id'])

        return comment_template.format(author=author['login'],
                                       author_url=author['html_url'],
                                       body=issue['body'],
                                       created_at=comment['created_at'],
                                       url=comment_url)


def migrate(src, dst, repo):
    return IssueMigrator(src, dst, repo).migrate()


def _get_author(client, login):
    return client.get('/users/{0}'.format(login)).json

