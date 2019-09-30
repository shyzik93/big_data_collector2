from . import sqltools
import copy

class Table:

    def __init__(self, db, tname, tfields, tname_prefix=''):

        self.db = db
        self.sqltools = sqltools.SQLTools(self.db)

        self.tname = tname
        self.tname_prefix = tname_prefix

        self.name = tname_prefix + tname

        #self.tfields = copy.deepcopy(tfields)
        tfields['id'] = 'INTEGER PRIMARY KEY AUTOINCREMENT'
        tfields['is_deleted'] = 'INTEGER NOT NULL DEFAULT \'0\' '
        tfields['date_add'] = 'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'

        self.tfs = {}
        for fname, v in tfields.items():
            tf = {
                'name': None,
                'type': None,
                'notnull': False,
                'unique': False,
                'foreign':False,
                'foreign_table': None,
                'foreign_field': None,
                'autoincr': False,
                'default': None,
                'primary_key': False,
            }

            fmeta = v.lower().split()
            while len(fmeta) != 1:
                e = fmeta.pop()

                if e.startswith('ref('):
                    foreign_table = e[4:-1].strip()
                    #if '.' in foreign_table:
                    foreign_table, foreign_field = foreign_table.split('.')
                    #else:
                    #    foreign_field = 'id'
                    tf['foreign'] = True
                    tf['foreign_table'] = foreign_table
                    tf['foreign_field'] = foreign_field # псевдоним
                elif e == 'unique':
                    tf['unique'] = True
                elif e == 'null':
                    fmeta.pop()
                    tf['notnull'] = True
                elif e == 'autoincrement':
                    tf['autoincr'] = True
                elif len(fmeta) > 1 and fmeta[-1] == 'default':
                    tf['default'] = e
                elif fmeta[-1] == 'primary' and e == 'key':
                    fmeta.pop()
                    tf['primary_key'] = True

            tf['type'] = fmeta.pop()

            orig_name = self.tname+'_'+fname
            if tf['foreign']: orig_name += '_id'
            tf['name'] = orig_name

            #print('    ', tf)

            self.tfs[fname] = tf

        self.foreigns = []

    def __getitem__(self, fname):
        return self.tfs[fname]['name']

    def is_field_foreign(self, fname):

       return self.tfs[fname]['foreign']

    def is_field_unique(self, fname):

       return self.tfs[fname]['unique']

    def get_foreign_field(self, fname):
        ''' Только, если мы уверены в наличии внешнего ключа '''

        return self.tfs[fname]['foreign_table'], self.tfs[fname]['foreign_field']

    def build_field(self, fname):

        fmeta = []

        if self.tfs[fname]['notnull']:
            fmeta.append('not null')
        if self.tfs[fname]['unique']:
            fmeta.append('unique')
        if self.tfs[fname]['primary_key']:
            fmeta.append('primary key')
        if self.tfs[fname]['autoincr']:
            fmeta.append('autoincrement')
        if self.tfs[fname]['default'] is not None:
            fmeta.append('default '+self.tfs[fname]['default'])

        if self.tfs[fname]['foreign']:
            self.foreigns.append(f"foreign key({self.tfs[fname]['name']}) references {self.tfs[fname]['foreign_table']}({self.tfs[fname]['foreign_table']}_id)")

        fmeta = ' '.join(fmeta)

        return f"`{self.tfs[fname]['name']}` {self.tfs[fname]['type']} {fmeta}"

    def build_create(self):

        fields = []
        self.foreigns = []

        for fname in self.tfs:
            fields.append(self.build_field(fname))

        fields += self.foreigns

        fields = ',\n    '.join(fields)

        return f"CREATE TABLE IF NOT EXISTS `{self.name}` (\n    {fields}\n);"

    def build_drop(self):

        return f"DROP TABLE IF EXISTS `{self.name}`;"

    def create(self):

        #print(self.build_create())
        self.db.execute(self.build_create())

    def select(self, keys, where):

        #print('    ', self.tname, keys, where)

        return self.sqltools.select(self.name, keys, where, self)

    def insert(self, fields):

        if len(fields) == 1:

            k, v = [i for i in fields.items()][0]

            kid = self.tfs['id']['name']#f'{self.tname}_id'
            if self.is_field_unique(k):
                k = self.tfs[k]['name']#f'{self.tname}_{k}'
                r = self.sqltools.select(self.name, kid, [[k, '=', v]]).fetchall()
                if r: return r[0][kid]

        return self.sqltools.insert(self.name, fields, None, self)

    def insert2(self, keys, values=None):
        ''' проверка на уникальность работает лишь для одного поля и одного значения '''

        if len(keys) == 1:

            if values is None:
                k, v = [i for i in keys.items()][0]
            else:
                k, v = (keys[0], values[0][0])

            kid = f'{self.tname}_id'
            if self.is_field_unique(k):
                k = f'{self.tname}_{k}'
                r = self.sqltools.select(self.name, kid, [[k, '=', v]]).fetchall()
                if r: return r[0][kid]

        '''if values is None:
            for k, v in keys.items():
                if not self.is_field_unique(k): continue
                r = self.sqltools.select(self.name, k, [[k, '=', v]]).fetchall()
                if r:
        '''

        '''if add_field_prefix:
            if values is None:
                pass
            else:
                pass
        '''

        return self.sqltools.insert(self.name, keys, values, self)

    def drop(self):

        self.db.execute(self.build_drop())

    def commit(self):

        self.db.commit()