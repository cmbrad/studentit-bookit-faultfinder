import sqlite3


class DatabaseManager(object):
	def __init__(self, filename):
		self.conn = sqlite3.connect(filename)

		self._create_tables()

	def _create_tables(self):
		self._create_fault_table()

	def _create_fault_table(self):
		table_def = \
		'''
		CREATE TABLE IF NOT EXISTS fault (
		id		INTEGER	PRIMARY KEY	AUTOINCREMENT,
		site_name	TEXT			NOT NULL,
		location_name	TEXT			NOT NULL,
		resource_name	TEXT			NOT NULL,
		fault_count	INT			NOT NULL
		);
		'''
		self.conn.execute(table_def)

	def update_fault(self, site_name, location_name, resource_name, fault_count):
		update_def = \
		'''
		INSERT OR REPLACE INTO fault (site_name, location_name, resource_name, fault_count)
		VALUES (?, ?, ?, ?)
		'''

		self.conn.execute(update_def, (site_name, location_name, resource_name, fault_count))

	def select_fault_count(self, site_name, location_name, resource_name):
		select_def = \
		'''
		SELECT * FROM fault WHERE site_name=? AND location_name=? AND resource_name=?
		'''
		cur = self.conn.cursor()
		cur.execute(select_def, (site_name, location_name, resource_name))

		row = cur.fetchone()
		return 0 if not row else row[4]

