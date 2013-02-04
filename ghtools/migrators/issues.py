import json
import logging

from ghtools.api import GithubAPIError

log = logging.getLogger(__name__)


def migrate(src, dst, name):
    src_issues = src.list_issues(name)
    dst_issues = dict((i['number'], i) for i in dst.list_issues(name))

    src_pulls = src.list_pulls(name)
    dst_pulls = dict((i['number'], i) for i in dst.list_pulls(name))

    try:
        for issue in src_issues:
            if issue['number'] not in dst_issues:
                payload = {
                    'title': issue['title'],
                    'body': generate_issue_body(issue),
                    # 'assignee':  issue['assignee'], # cannot migrate until users have been migrated
                    'milestone': issue['milestone'],
                    'labels': [label['name'] for label in issue['labels']]
                }
                dst_issue = dst.client.post('/repos/{0}/issues'.format(dst.full_name(name)), data=payload).json
                dst_issues[dst_issue['number']] = dst_issue

                add_comments(src, dst, name, issue)

            if issue['state'] != dst_issues[issue['number']]['state']:
                payload = {'state': issue['state']}
                dst.client.patch('/repos/{0}/issues/{1}'.format(dst.full_name(name), issue['number']), data=payload)

        for pull in src_pulls:
            try:
                if pull['number'] not in dst_pulls:
                    payload = {
                        'issue': pull['number'],
                        'head': pull['head']['sha'],
                        'base': pull['base']['sha']
                    }
                    dst_pull = dst.client.post('/repos/{0}/pulls'.format(dst.full_name(name)), data=payload).json
                    dst_pulls[dst_pull['number']] = dst_pull

                if pull['state'] != dst_pulls[pull['number']]['state']:
                    payload = {'state': pull['state']}
                    dst.client.patch('/repos/{0}/pulls/{2}'.format(dst.full_name(name), issue['number']), data=payload)
            except GithubAPIError as e:
                if e.response.status_code == 500:
                    log.error("Failed to migrate pull request, maybe the branch was deleted?")
                else:
                    raise
    except GithubAPIError as e:
        print(e.response.text)
        raise


def generate_issue_body(issue):
    return u"""**Migrated from github.com**\n[original]({0})\n\n{1}""".format(issue['html_url'], issue['body'])


def add_comments(src, dst, name, issue):
    for comment in src.client.get('/repos/{0}/issues/{1}/comments'.format(src.full_name(name), issue['number'])).json:
        payload = {
            'body': generate_comment_body(issue, comment)
        }
        dst.client.post('/repos/{0}/issues/{1}/comments'.format(dst.full_name(name), issue['number']), data=json.dumps(payload))


def generate_comment_body(issue, comment):
    return u"""**Migrated from github.com**\n[original]({0})\n\n{1}""".format(issue['html_url'], comment['body'])
