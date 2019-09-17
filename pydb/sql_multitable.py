from . import sql_table

class Multitable:

    def __init__(self, db, tables, table_prefix, show_log, uniq_keys):
        self.db = db

        self.show_log = show_log

        self.tables = {}
        for table in tables:
            _table = sql_table.Table(self.db, table['name'], table['fields'])
            self.tables[table['name']] = _table
            _table.create()
        self.db.commit()

    def insert(self, tname, fields):

        for fname, v in fields.items():
            fname = self.tables[tname].name+'_'+fname
            if not self.tables[tname].is_field_foreign(fname): continue
            foreign_table, foreign_value = self.tables[tname].get_foreign_field(fname)

            print(foreign_table, foreign_field)
            