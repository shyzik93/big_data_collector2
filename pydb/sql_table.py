from . import sqltools
import copy

class Table:

    def __init__(self, db, tname, tfields, tname_prefix=''):

        self.db = db
        self.sqltools = sqltools.SQLTools(self.db)

        self.tname = tname
        self.tname_prefix = tname_prefix

        self.name = tname_prefix + tname

        self.tfields = copy.deepcopy(tfields)
        self.tfields['id'] = 'INTEGER PRIMARY KEY AUTOINCREMENT'
        self.tfields['is_deleted'] = 'INTEGER NOT NULL DEFAULT \'0\' '
        self.tfields['date_add'] = 'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'

        '''for k in self.tfields.keys():
            self.tfields[k] = self.tfields[k]
            del self.tfields[k]
        '''

        self.foreigns = []

    def is_field_foreign(self, fname):

       fmeta = self.tfields[fname].split()
       return fmeta[-1].lower().startswith('ref')

    def is_field_unique(self, fname):

       fmeta = self.tfields[fname]
       return 'unique' in fmeta.lower()

    def get_foreign_field(self, fname):
        ''' Только, если мы уверены в наличии внешнего ключа '''

        fmeta = self.tfields[fname].split()
        foreign_table = fmeta[-1].split('(')[1][:-1]

        if '.' in foreign_table:
            foreign_table, foreign_field = foreign_table.split('.')
        else:
            foreign_field = foreign_table+'_id'

        return foreign_table, foreign_field

    def build_field(self, fname, fmeta):

        _fmeta = fmeta.split()
        if self.is_field_foreign(fname):
            _fmeta.pop()
            foreign_table, foreign_field = self.get_foreign_field(fname)
            self.foreigns.append(f'FOREIGN KEY({self.tname}_{fname}) REFERENCES {foreign_table}({foreign_field})')

        fmeta = ' '.join(_fmeta)

        return f"`{self.tname}_{fname}` {fmeta}"

    def build_create(self):

        fields = []
        self.foreigns = []

        #fields.append(self.build_field('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'))

        for fname, fmeta in self.tfields.items():
            fields.append(self.build_field(fname, fmeta))

        #fields.append(self.build_field({'is_deleted': 'INTEGER NOT NULL DEFAULT \'0\' '}))
        #fields.append(self.build_field('date_add', 'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'))

        fields += self.foreigns

        fields = ',\n    '.join(fields)

        return f"CREATE TABLE IF NOT EXISTS `{self.name}` (\n    {fields}\n);"

    def build_drop(self):

        return f"DROP TABLE IF EXISTS `{self.name}`;"

    def create(self):

        #print(self.build_create())
        self.db.execute(self.build_create())

    def insert(self, keys, values=None):
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

        return self.sqltools.insert(self.name, keys, values, self.name+'_')

    def drop(self):

        self.db.execute(self.build_drop())

    def commit(self):

        self.db.commit()