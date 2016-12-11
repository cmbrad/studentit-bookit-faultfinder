import logging
import time
from datetime import datetime

import click

from studentit.bookit.faultfinder import FaultFinder
from .db import DatabaseManager
from .email import send_fault_email


SECS_IN_DAY = 86400


@click.group()
@click.pass_context
def cli(ctx):
	configure_logging()
	ctx.obj['LOGGER'] = logging.getLogger('bookit.cli')


@cli.command()
@click.option('--username', envvar='BOOKIT_USERNAME', required=True)
@click.option('--password', envvar='BOOKIT_PASSWORD', required=True)
@click.option('--interval-secs', default=300)
@click.pass_obj
def find(obj, username, password, interval_secs):
	logger = obj['LOGGER']
	db_manager = DatabaseManager('faults.db')
	fault_finder = FaultFinder(username, password)

	while True:
		logger.info('Scanning for faults...')
		try:
			resources = fault_finder.scan()

			for resource, might_be_faulty in resources.items():
				site_name, location_name, resource_name = resource
				db_manager.update_fault(site_name, location_name, resource_name, might_be_faulty)
			logger.info('Finished scan. Waiting {interval} seconds to scan again.'.format(interval=interval_secs))
		except Exception as e:
			logger.info('Error during scan, cancelling. Waiting {interval} seconds to scan again.'.format(interval=interval_secs))
			logger.exception(e)

		time.sleep(interval_secs)


@cli.command()
@click.option('--limit-secs', default=SECS_IN_DAY*2.5, type=int)
@click.pass_obj
def list(obj, limit_secs):
	logger = obj['LOGGER']
	db_manager = DatabaseManager('faults.db')
	faulty = db_manager.select_faulty()

	for resource in faulty:
		age = datetime.now() - resource[4]
		if age.total_seconds() >= limit_secs:
			logger.info('{} {}'.format(resource, age))


@cli.command()
@click.option('--username', envvar='BOOKIT_USERNAME', required=True)
@click.option('--password', envvar='BOOKIT_PASSWORD', required=True)
@click.option('--limit-secs', default=SECS_IN_DAY*2.5, type=int)
@click.option('--to-email', required=True)
@click.pass_obj
def email(obj, username, password, limit_secs, to_email):
	logger = obj['LOGGER']
	db_manager = DatabaseManager('faults.db')
	faulty = db_manager.select_faulty()

	resources_to_email = []
	for resource in faulty:
		site_name, location_name, resource_name, start_time = resource
		age = datetime.now() - start_time

		if age.total_seconds() >= limit_secs:
			resources_to_email.append((site_name, location_name, resource_name, start_time, age))
	resources_to_email.sort(key=lambda x: (x[0], x[1], x[2]))
	send_fault_email(username, password, resources_to_email, to_email)


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

