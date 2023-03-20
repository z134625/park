from .api import apis


def api_register(api_func):
    for f in dir(api_func):
        if callable(eval(f'api_func.{f}')) and not f.startswith('__') and not f.endswith('__'):
            apis[f] = eval(f'api_func.{f}')
