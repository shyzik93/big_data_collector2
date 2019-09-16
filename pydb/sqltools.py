class SQLTools():

    def __init__(self, db):
        self.db = db

    def glue_fields(self, fields):
        ks = []
        vs = []
        for k, v in fields.items():
            ks.append(f"`{k}`=?")
            vs.append(v)
        return ', '.join(ks), vs

    def process_key(self, key, fname_prefix=''):
        if key == '*' or '(' in key or ' as ' in key.lower(): return key
        if not key.startswith('`'): key = '`'+fname_prefix+key
        if not key.endswith('`'): key = key+'`'
        return key

    def process_keys(self, keys, fname_prefix=''):
        if isinstance(keys, str):
            keys = [keys]
        for i, key in enumerate(keys):
            keys[i] = self.process_key(key, fname_prefix)
        return ','.join(keys)

    def process_cond(self, cond):
        #print('    cond2:', cond)
        key, op, value = cond
        if value is None:
            if op == '=': op = ' IS '
            elif op == '!=': op = ' is not '
        key = self.process_key(key)
        #print('    cond:', f'{key}{op}?', value)
        return f'{key}{op}?', value

    def process_where(self, where, main_op='AND'):
        #print('  where2:', where)
        if isinstance(where, tuple): # уже конвертированное
            return where[0], where[1]
        where_v = []
        for i, cond in enumerate(where):
            if isinstance(cond, str):
                continue # для выражений типа "`tbl1`.`field1`=`tbl2`.`field1`"
            cond, value = self.process_cond(cond)
            where[i] = cond
            where_v.append(value)
        #print('where:', f' {main_op} '.join(where), where_v)
        return f' {main_op} '.join(where), where_v

    def AND(self, where):
        return self.process_where(where, 'AND')

    def OR(self, where):
        return self.process_where(where, 'OR')

    def update(self, table, fields, where):

        table = self.process_key(table)

        where, where_v = self.process_where(where)#' AND '.join(where)

        ks, vs = self.glue_fields(fields)
        vs += where_v

        sql = f"UPDATE {table} SET {ks} WHERE {where}"
        self.db.execute(sql, tuple(vs))

    def insert(self, table, keys, values=None, fname_prefix=''):

        table = self.process_key(table)

        if isinstance(keys, dict):
            values = [list(keys.values())]
            keys = list(keys.keys())

        ks = self.process_keys(keys, fname_prefix)

        indexes = []

        for vs in values:
            _vs = ','.join(['?']*len(vs))
            sql = f"INSERT INTO {table} ({ks}) VALUES ({_vs})"
            #print(sql, '\n', tuple(vs))
            self.db.execute(sql, tuple(vs))
            indexes.append(self.db.lastrowid)

        return indexes[0] if len(indexes)==1 else indexes

    def select(self, tables, keys, where):

        tables = self.process_keys(tables)
        keys = self.process_keys(keys)
        where, where_v = self.process_where(where)#' AND '.join(where)

        sql = f"SELECT {keys} FROM {tables} WHERE {where}"
        #print(sql, '\n', where_v)
 
        if not isinstance(where_v, tuple): where_v = tuple(where_v)
        return self.db.execute(sql, where_v)

    def insert_uniq(self, table, keys, keys_uniq, primary_key, values=None):

        keys_uniq = self.process_keys(keys_uniq)

        if isinstance(keys, dict):
            values = list(keys.values())
            keys = list(keys.keys())

        where = []
        #where_v = []
        for i, key in enumerate(keys):
            if key not in keys_uniq: continue
            where.append([key, '=', values[i]])#(f'{key}=?')
            #where_v.append(values[i])

        r = self.select(table, primary_key, where).fetchall()
        if not r:
            return self.insert(table, keys, [values])
        else:
            return r[0][primary_key]