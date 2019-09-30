import requests
from init import sets

from pydb import sql_multitable
from pydb import db_binders
from pydb import sql_table
#from pydb import sqltools
from pyloader import saver_base
from pyloader import saver
import parsers

import configparser
import os.path

'''
import math
t = 0.118
a = 12.25
print('   ', (0.7276/t)*math.sin((a/2)*math.pi/180))
'''
#exit()

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
tables = ini2tables('tables.ini')
mtable = sql_multitable.Multitable(db, tables, sets['db_table_prefix'], sets['show_log'], None)
saver2 = saver_base.SaverSQL(mtable, sets['path_row_data'])
saver = saver.SaverSQL(mtable, sets['path_row_data'])

cfg = {
    'saver': saver,
    'tbls': mtable,
    'db': db,
}

parser = parsers.get('news_del_yeysk', cfg)
parser.run()

exit()

if __name__ == '__main__':
    
    db.export(sets['db_dump_to'])
    print(db)
    print(mtable.tables)
    
    print(mtable.tables['url'].build_drop())
    print(mtable.tables['url'].build_create())
    print(mtable.tables['url_title'].insert({'name':'ыыввв'}))
    #print(mtable.tables['url_title'].insert(['name'], [['длрв ег впл'], ['оооооо']]))
    print(mtable.tables['url_title'].insert({'name': 'длрв ег впл'}))
    print(mtable.tables['url_title'].insert({'name': 'оооооо'}))
    
    print(mtable.insert('url', {'scheme': 'https', 'domain': 'mail.ru', 'path': 'user/inbox.cgi', 'title': 'Ваша почта'}))
    
    print(saver2.save('my text', 'https://vk.com/user1/profile?audio=6', 'mytitle'))
    
    url = 'http://m.deleysk.ru'
    r = requests.get(url)
    print(saver.save(r, url))
    
    print(saver.exists( 'https://vk.com/user1/profile?audio=6'))
    r = saver.exists('http://m.deleysk.ru')
    print(r)
    if r:
        print(saver.open(r[1]))
    
    #a = 'bhuijb'
    #sql = "INSERT INTO `url_title` ('url_title_name') VALUES (?) WHERE NOT EXISTS (SELECT * FROM `url_title` WHERE `url_title_name` = ?)"
    #db.execute(sql, (a,a))
    
    #stable.tables['source_url'].drop()
    db.commit()
    
    