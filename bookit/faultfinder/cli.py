import time

import click

from bookit.faultfinder import FaultFinder
from .db import DatabaseManager


@click.group()
def cli():
	pass


@cli.command()
@click.option('--username', envvar='BOOKIT_USERNAME')
@click.option('--password', envvar='BOOKIT_PASSWORD')
@click.option('--interval-secs', default=10)
@click.option('--fault-limit', default=2)
def find(username, password, interval_secs, fault_limit):
	db_manager = DatabaseManager('faults.db')
	fault_finder = FaultFinder(username, password)

	while True:
		print('Scanning for faults...')
		potential_faults = fault_finder.scan()

		for resource, fault_count in potential_faults.items():
			site_name, location_name, resource_name = resource
			db_count = db_manager.select_fault_count(site_name, location_name, resource_name)
			total_count = db_count + fault_count
			print('Before', resource_name, db_manager.select_fault_count(site_name, location_name, resource_name))
			db_manager.update_fault(site_name, location_name, resource_name, total_count)
			print('After', resource_name, db_manager.select_fault_count(site_name, location_name, resource_name))

		time.sleep(interval_secs)

def main():
	cli()


if __name__ == '__main__':
	main()

