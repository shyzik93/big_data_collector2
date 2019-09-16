import sys
import os

sys.path.append(os.path.dirname(__file__))

def get_db_binder(db_type_name, sets_db):
    module = __import__('binder_'+db_type_name)
    return getattr(module, 'DBBinder')(sets_db)