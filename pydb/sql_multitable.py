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

    def __getitem__(self, tname):
        return self.tables[tname]

    def insert(self, tname, fields):

        # Заменяем значения на id

        for fname, v in fields.items():
            if not self.tables[tname].is_field_foreign(fname): continue
            foreign_table, foreign_field = self.tables[tname].get_foreign_field(fname)

            fields[fname] = self.tables[foreign_table].insert({foreign_field:v})

            #print(foreign_table, foreign_field, v_id)

        # Вставляем строку

        return self.tables[tname].insert(fields)

    def insert_unique(self, tname, fields, unique_keys=None):

        if unique_keys is None:
            unique_keys = fields.keys()

        # Заменяем значения на id

        for fname, v in fields.items():
            if not self.tables[tname].is_field_foreign(fname): continue
            foreign_table, foreign_field = self.tables[tname].get_foreign_field(fname)

            fields[fname] = self.tables[foreign_table].insert({foreign_field:v})

            #print(foreign_table, foreign_field, v_id)

        # Проверяем наличие дубликата

        where = []
        for key in unique_keys:
            where.append([self.tables[tname][key], '=', fields[key]])

        kid = self.tables[tname]['id']
        r = self.tables[tname].select(kid, where).fetchall()
        if r: return r[0][kid]

        # Вставляем строку

        return self.tables[tname].insert(fields)
            