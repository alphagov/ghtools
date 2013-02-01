
def migrate(src, dst, name):
	for hook in src.client.get('/repos/{0}/hooks'.format(src.full_name(name))).json:
		payload = {
			'name':   hook['name'],
			'config': hook['config'],
			'events': hook['events'],
			'active': hook['active']
		}
		dst.client.post('/repos/{0}/hooks'.format(dst.full_name(name)), data=payload)
