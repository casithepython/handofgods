import yaml

secrets = None
with open('secrets.yaml', 'r') as stream:
	try:
		secrets = yaml.safe_load(stream)
	except yaml.YAMLError as exc:
		raise 'Error: could not load client secrets'
