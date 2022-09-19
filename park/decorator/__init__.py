import re
import datetime
import warnings
import copy
from collections.abc import Iterable

from inspect import isclass, isfunction


class _Park(object):
    _register_number = 0
    _register_apps = {}
    _register_funcs = {}
    _exclude_apps = ['_CacheClass_0', '_CurrencySetting_1', '_ProgressPark_2', '_SelfStart_3',
                     '_RealTimeUpdate_4', '_ParkConcurrency_5', 'ParkQueue_6', 'ReClass_7',
                     '_ComputerSystem_10', '_GPUClass_11']
    _exclude_func = ['install_module_8', 'make_dir_or_doc_9']

    def __init__(self):
        self._exclude_mode = 3
        self._order_by = 'number'
        self._limit = None

    @classmethod
    def _register(cls, func=None, call: bool = False, **kwarg):
        """
        用于注册类或者函数，后续可使用park['']
        :param func:
        :param call:
        :param kwarg:
        :return:
        """
        if func:
            name = func.__name__
            if hasattr(func, '_name'):
                name = func._name
            result = {
                'number': cls._register_number,
                'func': func,
                'func_obj': None,
                'args': tuple(),
                'info': {
                    'module': func.__module__ if func.__module__ != '__main__' else 'this',
                    'doc': func.__doc__,
                    'name': func.__name__,
                },
                'create_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'process': None,
            }

            if isclass(func):
                cls._register_apps[name + '_' + str(cls._register_number)] = result
                cls._register_number += 1
            elif isfunction(func):

                cls._register_funcs[name + '_' + str(cls._register_number)] = result
                cls._register_number += 1

            def wrapper(*args, **kwargs):
                if func.__name__ in (tuple(cls._register_funcs.keys()) + tuple(cls._register_apps.keys())):
                    print('%s已注册成功' % func.__name__)
                else:
                    print('%s未注册成功' % func.__name__)
                return func(*args, **kwargs)

            return wrapper
        else:
            def wrapper(func_call):
                is_call = call
                func_arg = kwarg.get('arg', None)
                func_name = func_call.__name__
                if hasattr(func_call, '_name'):
                    func_name = func_call._name

                func_obj = tuple()

                if is_call and func_arg:
                    if isinstance(func_obj, dict):
                        func_obj = func_call(**func_arg)
                    else:
                        func_obj = func_call(*func_arg)
                elif is_call:
                    func_obj = func_call()
                func_result = {
                    'number': cls._register_number,
                    'func': func_call,
                    'func_obj': func_obj,
                    'args': func_arg,
                    'info': {
                        'module': func_call.__module__ if func_call.__module__ != '__main__' else 'this',
                        'doc': func_call.__doc__,
                        'name': func_call.__name__,
                    },
                    'create_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'process': None,
                }
                if isclass(func_call):
                    cls._register_apps[func_name + '_' + str(cls._register_number)] = func_result
                    cls._register_number += 1
                elif isfunction(func_call):
                    cls._register_funcs[func_name + '_' + str(cls._register_number)] = func_result
                    cls._register_number += 1

                def warp(*args, **kwargs):
                    if func_obj.__name__ in (tuple(cls._register_funcs.keys()) + tuple(cls._register_apps.keys())):
                        print('%s已注册成功' % func_obj.__name__)
                    else:
                        print('%s未注册成功' % func_obj.__name__)

                return warp

            return wrapper

    def _inherit(self, **kwarg):
        def wrapper(func):
            parent = kwarg.get('parent', None)
            number = kwarg.get('number', None)
            warn = kwarg.get('warn', False)
            assert parent, '必须指定父类'
            app = self[parent]

            if isinstance(app, list) and app.__len__() > 1 and not number:
                app = self[parent][0]
                if not warn:
                    warnings.warn('%s 该父类有多个， 默认取编号第一位的父类 %s' % (parent, app),
                                  RuntimeWarning, stacklevel=2)
            elif not isinstance(app, list):
                app = app
            if isinstance(number, int):
                app = self[parent][number]
            app_arg = app.args
            app = app.app

            if not isclass(app):
                raise ValueError('(%s) 方法不支持继承函数使用该装饰器(inherit)' % func.__name__)

            def warp(*args, **kwargs):
                parent_class = (object,)
                if isclass(func) and isclass(app):
                    parent_class = (func, app)
                elif isclass(func):
                    parent_class = (func,)
                elif isclass(app):
                    parent_class = (app,)

                class NewClass(*parent_class):
                    _describe = '此方法继承自%s' % app.__name__
                    func = {}

                    def __init__(self, app_args):
                        if app_args and isclass(app):
                            app.__init__(*app_args)
                        elif isfunction(app):
                            self.func[app.__name__] = app
                        if isclass(func):
                            func.__init__(self, *args, **kwargs)
                        elif isfunction(func):
                            self.func[func.__name__] = func

                    def __getattr__(self, item):
                        res = re.search('([a-zA-Z_]+?)__sub$', item)
                        if item in self.func or (res and res.group(1) in self.func):
                            return self.func[item] if item in self.func else self.func[res.group(1)]
                        else:
                            for obj in parent_class:
                                no1 = super(obj, self).__getattr__(item)
                                if no1:
                                    return no1
                            return None

                    def __getitem__(self, item):
                        if item in self.func:
                            return self.func[item]
                        else:
                            super(NewClass, self).__getattr__(item)

                return NewClass(app_args=(self, *app_arg) if app_arg else (self,))

            return warp

        return wrapper

    def _get_exclude_list(self):
        func_keys = self._register_funcs.keys()
        app_keys = self._register_apps.keys()
        if self._exclude_mode == 1:
            func_keys = list(set(func_keys).difference(set(self._exclude_func)))
            app_keys = list(set(app_keys).difference(set(self._exclude_apps)))
        elif self._exclude_mode == 2:
            func_keys = list(set(func_keys).intersection(set(self._exclude_func)))
            app_keys = list(set(app_keys).intersection(set(self._exclude_apps)))
        return func_keys, app_keys

    def __getitem__(self, item):
        it, *types = item.split('__') if '__' in item else (item, [''])
        func_keys, app_keys = self._get_exclude_list()
        kwargs = {}
        if '.' in it:
            its = copy.deepcopy(it)
            it = it.split('.')[-1]
            kwargs['module'] = its.replace('.', '_')
        func_list = list(filter(lambda x: it in x, func_keys))
        app_list = list(filter(lambda x: it in x or it in dir(self._register_apps[x]['func']),
                               app_keys))
        order_mode = ''
        order_by = 'number'
        if self._order_by:
            order = re.split(r'\s+', self._order_by)
            order_by = order[0]
            if order.__len__() > 1:
                order_mode = order[1]
        func = []
        apps = []
        if func_list:
            func = [self._AppsFunc(self._register_funcs[key]) for key in sorted(func_list,
                                                                                key=lambda x: x.split('_')[1])]
        if app_list:
            apps = [self._AppsFunc(self._register_apps[key]) for key in sorted(app_list,
                                                                               key=lambda x: x.split('_')[1])]
        if not types:
            if func or apps:
                res = func + apps
                if self._limit:
                    res = res[:self._limit]
                if order_by == 'name':
                    res = sorted(res, key=lambda x: x.app.__name__)
                elif order_by == 'create_time':
                    res = sorted(res, key=lambda x: x.create_time)
                elif order_by == 'number':
                    res = sorted(res, key=lambda x: x.number)
                if order_mode.upper() == 'DESC':
                    res = res[::-1]
                return self._AppList(app=res, **kwargs)
            else:
                raise ImportError('(%s)该类或方法还未注册' % item)
        else:
            limit_list = list(filter(lambda x: 'limit' in x, types))
            order_by_list = list(filter(lambda x: 'order' in x, types))

            res = func + apps
            if 'app' in types and 'func' not in types:
                res = apps
            elif 'func' in types and 'app' not in types:
                res = func
            elif 'func' in types and 'app' in types or 'func' not in types and 'app' not in types:
                res = func + apps
            if self._limit:
                res = res[:self._limit]
            if order_by == 'name':
                res = sorted(res, key=lambda x: x.app.__name__)
            elif order_by == 'create_time':
                res = sorted(res, key=lambda x: x.create_time)
            elif order_by == 'number':
                res = sorted(res, key=lambda x: x.number)
            if order_mode.upper() == 'DESC':
                res = res[::-1]

            if limit_list:
                limit = limit_list[0]
                index = types.index(limit)
                numbers = re.search('^limit_(\d+)$', types[index])
                if numbers:
                    numbers = numbers.group(1)
                    kwargs['limit'] = numbers
                else:
                    raise ValueError("格式错误，应为limit_数字")
            if order_by_list:
                order_by = order_by_list[0]
                index = types.index(order_by)
                order_mode = re.search('^order_by_([a-zA-Z_]+)', types[index])
                order = 'number'
                mode = ''
                if order_mode:
                    order = order_mode.group(1)
                    *order, mode = order.rsplit('_')
                    order = '_'.join(order)
                if order == 'name':
                    res = sorted(res, key=lambda x: x.app.__name__)
                elif order == 'create_time':
                    res = sorted(res, key=lambda x: x.create_time)
                elif order == 'number':
                    res = sorted(res, key=lambda x: x.number)
                if mode.upper() == 'DESC':
                    res = res[::-1]
            return self._AppList(app=res, **kwargs)

    def __getattr__(self, item):
        order_mode = ''
        order_by = 'number'
        if self._order_by:
            order = re.split(r'\s+', self._order_by)
            order_by = order[0]
            if order.__len__() > 1:
                order_mode = order[1]
        func_keys, app_keys = self._get_exclude_list()
        func = [self._AppsFunc(self._register_funcs[key]) for key in sorted(func_keys,
                                                                            key=lambda x: x.split('_')[1])]
        apps = [self._AppsFunc(self._register_apps[key]) for key in sorted(app_keys,
                                                                           key=lambda x: x.split('_')[1])]
        if item not in dir(self):
            res = []
            if item == 'app' or item == 'apps':
                res = apps
            elif item == 'func' or item == 'funcs':
                res = func
            elif item == 'all' or True:
                res = func + apps

            if self._limit:
                res = res[:self._limit]
            if order_by == 'name':
                res = sorted(res, key=lambda x: x.app.__name__)
            elif order_by == 'create_time':
                res = sorted(res, key=lambda x: x.create_time)
            elif order_by == 'number':
                res = sorted(res, key=lambda x: x.number)
            if order_mode.upper() == 'DESC':
                res = res[::-1]
            return self._AppList(app=res)
        else:
            return super().__getattr__(item)

    class _AppsFunc:
        def __init__(self, obj: dict):
            self.app = obj['func']
            self.obj = obj['func_obj']
            self.args = obj['args']
            self.info = obj['info']
            self.number = obj['number']
            self.create_time = obj['create_time']
            self.func = dir(self.obj) if self.obj else dir(self.app)

        def __call__(self, *args, **kwargs):
            if callable(self.app) and (not self.obj or (args or kwargs)):
                return self.app(*args, **kwargs)
            elif self.obj:
                return self.obj
            else:
                return self.app

        def __iter__(self):
            return f"{self.info['module']}.{self.info['name']}"

        def __str__(self):
            return f"{self.info['module']}.{self.info['name']}"

        def __eq__(self, other):
            return self.number == other.number

        def __ne__(self, other):
            return self.number != other.number

        def __gt__(self, other):
            return self.number > other.number

        def __ge__(self, other):
            return self.number >= other.number

        def __lt__(self, other):
            return self.number < other.number

        def __le__(self, other):
            return self.number <= other.number

        def __bool__(self):
            if self.app:
                return True
            else:
                return False

        def __getattr__(self, item):
            if item == 'info':
                return self.info
            elif item == 'doc':
                return self.info['doc']
            elif item == 'name':
                return self.info['name']
            elif item == '_module':
                return self.info['module']
            elif item == 'value':
                return self.obj
            elif item == '_name':
                return self.app.__name__
            elif item in self.func:
                attr = eval(f'self.obj.{item}')
                return attr
            elif item == self.app.__name__ and self.obj:
                return self.obj
            elif item == self.app.__name__:
                return self.app
            else:
                return super().__getattr__(item)

    class _AppList:
        _app_list = []

        def __init__(self, app, limit=None, module=None):
            self._app_list = []
            if not isinstance(app, Iterable):
                self._app_list.append(app)
            else:
                for item in app:
                    if item not in self._app_list:
                        self._app_list.append(item)
            self._length = len(self._app_list)
            self._start = 0
            self._step = 1
            if limit:
                self._app_list = self._app_list[:int(limit)]
            if module:
                # if not self._app_list:
                app_func_list = []
                for _app in self._app_list:
                    for _app_func in _app.func:

                        names = "%s_%s_%s" % (_app._name, _app_func, _app.number)
                        if module in names:
                            app_func_list.append(_app)
                if not app_func_list:
                    self._app_list = list(filter(lambda x: module in "%s_%s_%s" % (x._module, x._name, x.number),
                                                 self._app_list))
                else:
                    self._app_list = app_func_list

        def __call__(self, *args, **kwargs):
            if self._app_list.__len__() == 1:
                return self._app_list[0](*args, **kwargs)
            else:
                raise IndexError("有多个应用请指定")

        def __getitem__(self, item):
            if isinstance(item, int):
                return self._app_list[item]
            else:
                return super().__getitem__(item)

        def __str__(self):
            return f'AppList({",".join(["%s_%s_%s" % (attr._module, attr._name, attr.number) for attr in self._app_list])})'

        def __getattr__(self, item):
            if item in dir(self):
                return super().__getattr__(item)
            for attr in self._app_list:
                try:
                    return eval(f'attr.{item}')
                except AttributeError:
                    return None

        def __len__(self):
            return len(self._app_list)

        def __iter__(self):
            return self

        def __next__(self):
            obj = self._app_list
            self._start += self._step
            if self._start > self._length:
                raise StopIteration
            else:
                return obj[self._start - 1]

        def __bool__(self):
            if self._app_list:
                return True
            else:
                return False


class Park(_Park):
    EXCLUDE_SYS = 1
    EXCLUDE_SELF = 2
    EXCLUDE_DEFAULT = 3

    def __call__(self, exclude=3, order='number', limit=None, *args, **kwargs):
        self._exclude_mode = exclude
        self._order_by = order
        self._limit = limit
        return self

    @classmethod
    def _register_function(cls, func=None, call: bool = False, **kwarg):
        is_call = call
        func_arg = kwarg.get('arg', None)
        queue_task = kwarg.get('task', False)
        func_name = func.__name__
        if hasattr(func, '_name'):
            func_name = func._name

        func_obj = tuple()
        if not queue_task:
            if is_call and func_arg:
                if isinstance(func_obj, dict):
                    func_obj = func(**func_arg)
                else:
                    func_obj = func(*func_arg)
            elif is_call:
                func_obj = func()
            func_result = {
                'number': cls._register_number,
                'func': func,
                'func_obj': None,
                'args': tuple(),
                'info': {
                    'module': func.__module__ if func.__module__ != '__main__' else 'this',
                    'doc': func.__doc__,
                    'name': func.__name__,
                },
                'create_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'process': None,
            }
        else:
            func_result = {

            }
        if isclass(func):
            cls._register_apps[func_name + '_' + str(cls._register_number)] = func_result
            cls._register_number += 1
        elif isfunction(func):
            cls._register_funcs[func_name + '_' + str(cls._register_number)] = func_result
            cls._register_number += 1

    def register(self, apps, kwargs=None):
        if kwargs is None:
            kwargs = {}
        if type(apps).__name__ == 'module':
            index_app = dir(apps).index('__builtins__')
            index_func = dir(apps).index('__spec__')
            funcs = dir(apps)[:index_app] + dir(apps)[index_func + 1:]
            for func in funcs:
                if type(eval(f'apps.{func}')).__name__ != 'module':
                    self._register_function(func=eval(f'apps.{func}'), **kwargs)
        else:
            if isinstance(apps, Iterable):
                for app in apps:
                    if type(app).__name__ == 'module':
                        index = dir(apps).index('__builtins__')
                        funcs = dir(apps)[:index]
                        for func in funcs:
                            self._register_function(func=eval(f'apps.{func}'), **kwargs)
                    else:
                        self._register_function(func=app, **kwargs)
            else:
                self._register_function(func=apps, **kwargs)

    def task(self, func, app=None, mode=0, timing=None):
        item = func
        if app:
            item = f'{app}.{func}'
        function = self[item]


park = Park()
registers = park.register
register = park._register
inherit = park._inherit
