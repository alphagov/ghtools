def migrate(src, dst):
    for hook in src.list_hooks():
        payload = {
            'name': hook['name'],
            'config': hook['config'],
            'events': hook['events'],
            'active': hook['active']
        }
        dst.create_hook(payload)

