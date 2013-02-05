import textwrap


def migrate(src, dst):
    for comment in src.list_commit_comments():
        author_login = comment['user']['login']
        author = src.client.get('/users/{0}'.format(author_login)).json
        body = _generate_comment_body(author, comment)

        payload = {
            'body': body,
            'path': comment['path'],
            'position': comment['position'],
            'line': comment['line']
        }

        dst.create_commit_comment(comment['commit_id'], payload)


def _generate_comment_body(author, comment):
    comment_template = textwrap.dedent(u"""
    <a href="{author_url}">{author}</a>: {body}

    <em><a href="{url}">Original comment</a> created at {created_at}.</em>
    """)

    return comment_template.format(author=author['login'],
                                   author_url=author['html_url'],
                                   body=comment['body'],
                                   url=comment['html_url'])
