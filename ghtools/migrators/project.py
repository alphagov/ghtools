
def migrate(src, dst, name):
	dst.create_project(src.get_project(name).json)
	
