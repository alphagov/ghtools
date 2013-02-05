import logging
import textwrap

from ghtools.exceptions import GithubAPIError

log = logging.getLogger(__name__)


class IssueMigrator(object):

    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def migrate(self):
        log.debug("Migrating %s to %s -> issues", self.src, self.dst)

        issues = self.src.list_issues(include_closed=True)
        sorted_issues = sorted(issues, key=lambda x: x['number'])
        for issue in sorted_issues:
            self._migrate_issue(issue)

        pulls = self.src.list_pulls(include_closed=True)
        sorted_pulls = sorted(pulls, key=lambda x: x['number'])
        for pull in sorted_pulls:
            self._migrate_pull(pull)

    def _migrate_issue(self, issue):
        log.debug("Migrating %s to %s -> issues -> #%s", self.src, self.dst, issue['number'])

        payload = {
            'title': issue['title'],
            'body': self._generate_issue_body(issue),
            # 'assignee':  issue['assignee'], # cannot migrate until users have been migrated
            'milestone': issue['milestone'],
            'labels': [label['name'] for label in issue['labels']]
        }

        self.dst.create_issue(payload)

        issue_comments = self.src.list_issue_comments(issue)
        sorted_comments = sorted(issue_comments, key=lambda x: x['created_at'])

        should_close = (issue['state'] == 'closed')

        for comment in sorted_comments:
            if should_close and comment['created_at'] > issue['closed_at']:
                self.dst.close_issue(issue)
                should_close = False

            payload = {'body': self._generate_comment_body(issue, comment)}
            self.dst.create_issue_comment(issue, payload)

        if should_close:
            self.dst.close_issue(issue)

    def _migrate_pull(self, pull):
        log.debug("Migrating %s to %s -> issues -> PR #%s", self.src, self.dst, pull['number'])

        payload = {
            'issue': pull['number'],
            'head': pull['head']['sha'],
            'base': pull['base']['sha']
        }

        try:
            self.dst.create_pull(payload)
        except GithubAPIError as e:
            if e.response.status_code == 500:
                log.error("Failed to migrate pull request, maybe the branch was deleted?")
            else:
                raise

    def _generate_issue_body(self, issue):
        issue_template = textwrap.dedent(u"""
        <a href="{author_url}">{author}</a>: {body}

        <em><a href="{url}">Original issue</a> ({shortname}) created at {created_at}.</em>
        """)

        author = _get_author(self.src.client, issue['user']['login'])
        shortname = '{0}#{1}'.format(self.src.org_repo, issue['number'])

        return issue_template.format(author=author['login'],
                                     author_url=author['html_url'],
                                     body=issue['body'] or 'No description given.',
                                     created_at=issue['created_at'],
                                     url=issue['html_url'],
                                     shortname=shortname)

    def _generate_comment_body(self, issue, comment):
        comment_template = textwrap.dedent(u"""
        <a href="{author_url}">{author}</a>: {body}

        <em><a href="{url}">Original comment</a> created at {created_at}.</em>
        """)

        author = _get_author(self.src.client, comment['user']['login'])
        comment_url = '{0}#issuecomment-{1}'.format(issue['html_url'], comment['id'])

        return comment_template.format(author=author['login'],
                                       author_url=author['html_url'],
                                       body=comment['body'],
                                       created_at=comment['created_at'],
                                       url=comment_url)


def migrate(src, dst):
    return IssueMigrator(src, dst).migrate()


def _get_author(client, login):
    return client.get('/users/{0}'.format(login)).json

