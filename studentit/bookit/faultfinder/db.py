import sqlite3

from datetime import datetime


class DatabaseManager(object):
	def __init__(self, filename):
		self.conn = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

		self._create_tables()

	def _create_tables(self):
		self._create_fault_table()
		self._create_control_table()

	def _create_fault_table(self):
		table_def = \
		'''
		CREATE TABLE IF NOT EXISTS fault (
		id		INTEGER	PRIMARY KEY	AUTOINCREMENT,
		site_name	TEXT			NOT NULL,
		location_name	TEXT			NOT NULL,
		resource_name	TEXT			NOT NULL,
		fault_begin	TIMESTAMP
		);
		'''
		self.conn.execute(table_def)
		self.conn.commit()

	def _create_control_table(self):
		table_def = \
		'''
		CREATE TABLE IF NOT EXISTS control (
		id		INTEGER PRIMARY KEY	AUTOINCREMENT,
		last_update	TIMESTAMP
		);
		'''
		self.conn.execute(table_def)
		self.conn.commit()

	def update_fault(self, site_name, location_name, resource_name, might_be_faulty):
		insert_def = \
		'''
		INSERT INTO fault (site_name, location_name, resource_name, fault_begin)
		VALUES (?, ?, ?, ?)
		'''

		update_def = \
		'''
		UPDATE fault SET fault_begin = ?
		WHERE site_name = ? AND location_name = ? AND resource_name = ?
		'''

		fault = self._select_fault(site_name, location_name, resource_name)
		if fault:
			update_time = fault[4] if might_be_faulty else None
			update_time = datetime.now() if might_be_faulty and update_time is None else update_time
			self.conn.execute(update_def, (update_time, site_name, location_name, resource_name))
		else:
			self.conn.execute(insert_def, (site_name, location_name, resource_name, datetime.now() if might_be_faulty else None))

		self.conn.commit()

	def select_faulty(self):
		select_def = \
		'''
		SELECT site_name, location_name, resource_name, fault_begin FROM fault
		WHERE fault_begin IS NOT NULL
		ORDER BY site_name, location_name, resource_name;
		'''
		cur = self.conn.cursor()
		cur.execute(select_def)
		
		return cur.fetchall()

	def _select_fault(self, site_name, location_name, resource_name):
		select_def = \
		'''
		SELECT * FROM fault WHERE site_name=? AND location_name=? AND resource_name=?
		'''
		cur = self.conn.cursor()
		cur.execute(select_def, (site_name, location_name, resource_name))

		return cur.fetchone()

