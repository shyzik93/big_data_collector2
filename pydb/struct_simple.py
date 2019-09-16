from . import sql_table

class SSimple:

    def __init__(self, db, tables, table_prefix, show_log, uniq_keys):
        self.db = db

        self.show_log = show_log

        self.tables = {}
        for table in tables:
            _table = sql_table.Table(self.db, table['name'], table['fields'])
            self.tables[table['name']] = _table
            _table.create()
        self.db.commit()

    def add_row(self, fields):

        main_table = 'source_url'

        for name, values in fields.items():
            if not self.tables[main_table].is_field_foreign(name): continue
            