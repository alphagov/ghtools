import logging
import textwrap

from ghtools.exceptions import GithubAPIError

log = logging.getLogger(__name__)


class IssueMigrator(object):

    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def migrate(self):
        log.info("Migrating %s to %s -> issues", self.src, self.dst)

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

        if pull['head']['sha'] == pull['base']['sha']:
            log.warn('Skipping pull request migration: PR#%s', pull['number'])
            log.warn('Not creating PR with head.sha == base.sha (%s, %s)', pull['head']['sha'], pull['base']['sha'])
            return

        # Attempt to create a pull request on the basis of human-readable
        # refs first.
        try:
            self.dst.create_pull({'issue': pull['number'],
                                  'head': pull['head']['ref'],
                                  'base': pull['base']['ref']})
        except GithubAPIError:
            # Attempt to create a pull request with at least one
            # human-readable ref
            try:
                self.dst.create_pull({'issue': pull['number'],
                                      'head': pull['head']['sha'],
                                      'base': pull['base']['ref']})

            # Fall back to just creating the pull request with shas instead of
            # refs
            except GithubAPIError:
                self.dst.create_pull({'issue': pull['number'],
                                      'head': pull['head']['sha'],
                                      'base': pull['base']['sha']})

        # Add a note to tell people if the PR was ever merged
        if pull.get('merged_at'):
            merged_by = ''
            if 'merged_by' in pull and pull['merged_by']['type'] == 'User':
                author = _get_author(self.src.client, pull['merged_by']['login'])
                merged_by = ' by [{0}]({1})'.format(author['login'], author['html_url'])

            merged_in = ''
            if 'merge_commit_sha' in pull:
                merged_in = ' in {0}'.format(pull['merge_commit_sha'])

            comment = {'body': '*Merged{0} at {1}{2}*'.format(merged_by, pull['merged_at'], merged_in)}
            self.dst.create_issue_comment(pull, comment)

    def _generate_issue_body(self, issue):
        issue_template = textwrap.dedent(u"""
        <a href="{author_url}">{author}</a>:
        {body}

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
        <a href="{author_url}">{author}</a>:
        {body}

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


def _get_author(client, login, _author_memo={}):
    if login not in _author_memo:
        _author_memo[login] = client.get('/users/{0}'.format(login)).json()
    return _author_memo[login]
