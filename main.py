from init import sets

from pydb import sql_multitable
from pydb import db_binders
from pydb import sql_table
#from pydb import sqltools

import configparser
import os.path

def ini2tables(tables_file):
    config = configparser.ConfigParser()
    config.read(os.path.join('configs', tables_file))
    
    tables = []
    for section_name in config:
        if section_name == 'DEFAULT': continue
        table = {'name': section_name, 'fields':{}}
        
        #print(section_name)
        
        for k, v in config[section_name].items():
            #print('   ', k, v)
            table['fields'][k] = v
        
        tables.append(table)
        
    return tables

'''
Для командной строки:
+ экспорт/импорт базы
+ запуск парсера
'''

db = db_binders.get_db_binder(sets['db_type'], sets['db_sets'][sets['db_type']])

#db = pydb.DB(sets)

if __name__ == '__main__':
    
    db.export(sets['db_dump_to'])
    print(db)
    
    tables = ini2tables('tables.ini')
    stable = sql_multitable.Multitable(db, tables, sets['db_table_prefix'], sets['show_log'], None)
    print(stable.tables)
    
    print(stable.tables['url'].build_drop())
    print(stable.tables['url'].build_create())
    print(stable.tables['url_title'].insert({'name':'ыыввв'}))
    print(stable.tables['url_title'].insert(['name'], [['длрв ег впл'], ['оооооо']]))
    
    stable.insert('url', {'schema': 'https', 'domain': 'mail.ru', 'path': 'user/inbox.cgi', 'title': 'Ваша почта'})
    
    #stable.tables['source_url'].drop()
    db.commit()
    
    