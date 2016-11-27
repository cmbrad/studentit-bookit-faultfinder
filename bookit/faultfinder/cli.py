import time
import logging
from datetime import datetime

import click

from bookit.faultfinder import FaultFinder
from .db import DatabaseManager


SECS_IN_DAY = 86400


@click.group()
@click.pass_context
def cli(ctx):
	configure_logging()
	ctx.obj['LOGGER'] = logging.getLogger('bookit.cli')


@cli.command()
@click.option('--username', envvar='BOOKIT_USERNAME')
@click.option('--password', envvar='BOOKIT_PASSWORD')
@click.option('--interval-secs', default=300)
@click.option('--fault-limit', default=2)
@click.pass_obj
def find(obj, username, password, interval_secs, fault_limit):
	logger = obj['LOGGER']
	db_manager = DatabaseManager('faults.db')
	fault_finder = FaultFinder(username, password)

	while True:
		logger.info('Scanning for faults...')
		potential_faults = fault_finder.scan()

		for resource, fault_count in potential_faults.items():
			site_name, location_name, resource_name = resource
			db_count = db_manager.select_fault_count(site_name, location_name, resource_name)

			total_count = (db_count + fault_count) if fault_count == 1 else 0
			#print('Before', resource_name, db_manager.select_fault_count(site_name, location_name, resource_name))
			db_manager.update_fault(site_name, location_name, resource_name, total_count)
			#print('After', resource_name, db_manager.select_fault_count(site_name, location_name, resource_name))

		logger.info('Finished scan. Waiting {interval} seconds to scan again.'.format(interval=interval_secs))
		time.sleep(interval_secs)


@cli.command()
@click.option('--limit-secs', default=SECS_IN_DAY*2.5, type=int)
@click.pass_obj
def list(obj, limit_secs):
	logger = obj['LOGGER']
	db_manager = DatabaseManager('faults.db')
	faulty = db_manager.select_faulty()

	for resource in faulty:
		resource_name, site_name, location_name = resource[0], resource[1], resource[2]
		fault_count = resource[3]
		fault_begin = resource[4]
		age = datetime.now() - resource[4]

		if age.total_seconds() >= limit_secs:
			logger.info('{} {}'.format(resource, age))


def configure_logging():
	# create logger
	logger = logging.getLogger('bookit')
	logger.setLevel(logging.DEBUG)

	# create console handler and set level to debug
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)

	# create formatter
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	# add formatter to ch
	ch.setFormatter(formatter)

	# add ch to logger
	logger.addHandler(ch)


def main():
	cli(obj={}, auto_envvar_prefix='BOOKIT')


if __name__ == '__main__':
	main()

