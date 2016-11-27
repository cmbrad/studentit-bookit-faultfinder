from collections import defaultdict

from bookit.api_client import ApiClient


class FaultFinder(object):
	def __init__(self, username, password, interval=60, site_id=None):
		self.site_id = site_id
		self.client = ApiClient(username, password)

		self._potential_faults = defaultdict(int)

	def scan(self):
		all_status = self.client.admin_all_resource_status()
		for site in all_status:
			# Don't track default site - not in use by students
			# and half of them don't physically exist
			if site['name'] == '_default':
				continue

			for location in site['locations']:
				for resource in location['resources']:
					resource_identifier = site['name'], location['name'], resource['name']
					if self._should_track_resource(resource):
						self._potential_faults[resource_identifier] = 1
					else:
						self._potential_faults[resource_identifier] = 0

		return self._potential_faults

	def _should_track_resource(self, resource):
		name_lower = resource['name'].lower()
		is_off = resource['admin_status'] == 'Switched Off or No Communication'

		not_room = 'room' not in name_lower
		not_booth = 'booth' not in name_lower
		not_game = 'game' not in name_lower

		return is_off and not_room and not_booth and not_game

