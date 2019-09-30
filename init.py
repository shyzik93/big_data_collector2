import os.path

# указываем пути

cdir = os.path.dirname(__file__)

sets = {
    'db_table_prefix': 'parser_',
    'db_dump_to': os.path.join(cdir, 'dump.sql'),
    'db_type': 'sqlite3',
    'db_sets': {
        'sqlite3': {
            'path': os.path.join(cdir, 'main.db'),
        },
        'mysql': {
            'host': '',
            'name': '',
            'user': '',
            'password': '',
            'port': 0
        }
    },
    'path_row_data': os.path.join(cdir, 'data_loaded'),
    'path_export_data': os.path.join(cdir, 'data_export'),
    'show_log': True,
}

