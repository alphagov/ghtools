import json

def migrate(src, dst, name):
	for comment in src.client.get('/repos/{0}/comments'.format(src.full_name(name))).json:
		payload = {
			'body':      generate_body(comment),
			'path':      comment['path'],
			'position':  comment['position'],
			'line':      comment['line']
		}

		dst.client.post('/repos/{0}/commits/{1}/comments'.format(dst.full_name(name), comment['commit_id']), data=payload)

def generate_body(comment):
	return u"**Migrated from github.com**\n[original]({0})\n\n{1}".format(comment['html_url'], comment['body'])