import os, sys

_path = os.path.dirname(__file__)
sys.path.append(_path)

def get(module_name, cfg):
    module = __import__(module_name)
    return getattr(module, 'Parser')(cfg)
