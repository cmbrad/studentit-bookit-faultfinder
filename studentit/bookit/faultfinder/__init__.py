from collections import defaultdict

from studentit.bookit.api import ApiClient


class FaultFinder(object):
	def __init__(self, username, password, interval=60, site_id=None):
		self.site_id = site_id
		self.client = ApiClient(username, password)

	def scan(self):
		resources = defaultdict(bool)

		all_status = self.client.admin_all_resource_status()
		for site in all_status:
			# Don't track default site - not in use by students
			# and half of them don't physically exist
			if site['name'] == '_default':
				continue

			for location in site['locations']:
				for resource in location['resources']:
					resource_identifier = site['name'], location['name'], resource['name']
					resources[resource_identifier] = self._resource_might_be_faulty(resource)

		return resources

	def _resource_might_be_faulty(self, resource):
		name_lower = resource['name'].lower()
		is_off = resource['admin_status'] == 'Switched Off or No Communication'

		not_room = 'room' not in name_lower
		not_booth = 'booth' not in name_lower
		not_game = 'game' not in name_lower

		return is_off and not_room and not_booth and not_game
