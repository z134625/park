import json
import re
import datetime
import warnings
import copy
from collections.abc import Iterable

from inspect import isclass, isfunction
from multiprocessing import Pool, Process
from threading import Thread
import asyncio


class _AppsFunc:
    """
    每一个注册的应用重新包装的函数，以便进行统一的排序、属性
    """

    def __init__(self, obj, args=None):
        if isinstance(obj, dict):
            self._app = obj['func']
            self._obj = obj['func_obj']
            self._args = obj['args']
            self._info = obj['info']
            self._number = obj['number']
            self._create_time = obj['create_time']
            self._func = dir(self._obj) if self._obj else dir(self._app)
        elif isclass(obj) or isfunction(obj):
            self._app = obj
            self._obj = obj(**args) if args else obj()
            self._args = args
            self._info = {'module': obj.__module__, 'name': obj.__name__, 'doc': obj.__doc__}
            self._number = None
            self._create_time = datetime.datetime.now()
            self._func = dir(self._obj) if self._obj else dir(self._app)

    def __call__(self, *args, **kwargs):
        if callable(self._app) and (not self._obj or (args or kwargs)):
            return self._app(*args, **kwargs)
        elif self._obj:
            return self._obj
        else:
            return self._app

    def __iter__(self):
        return f"{self._info['module']}.{self._info['name']}"

    def __str__(self):
        return f"{self._info['module']}.{self._info['name']}"

    def __eq__(self, other):
        return self._number == other._number

    def __ne__(self, other):
        return self._number != other._number

    def __gt__(self, other):
        return self._number > other._number

    def __ge__(self, other):
        return self._number >= other._number

    def __lt__(self, other):
        return self._number < other._number

    def __le__(self, other):
        return self._number <= other._number

    def __bool__(self):
        if self._app:
            return True
        else:
            return False

    @property
    def info(self):
        return self.__getattr__('info')

    @property
    def doc(self):
        return self.__getattr__('doc')

    @property
    def name(self):
        return self.__getattr__('name')

    @property
    def value(self):
        return self.__getattr__('value')

    def __getattr__(self, item):
        if item == 'info':
            return self._info
        elif item == 'doc':
            return self._info['doc']
        elif item == 'name':
            return self._info['name']
        elif item == '_module':
            return self._info['module']
        elif item == 'value':
            return self._obj
        elif item == '_name' and item not in self._func:
            return self._app.__name__
        elif item == '_number':
            return self._number
        elif item in self._func:
            if self._obj:
                attr = eval(f'self._obj.{item}')
            else:
                attr = eval(f'self._app.{item}')
            return attr
        elif item == self._app.__name__ and self._obj:
            return self._obj
        elif item == self._app.__name__:
            return self._app
        else:
            try:
                if self._obj:
                    attr = eval(f'self._obj.{item}')
                else:
                    attr = eval(f'self._app.{item}')
                return attr
            except AttributeError:
                raise AttributeError(f'{str(self.__class__.__name__)} not have this attr')


class _AppList:
    _app_list = []

    def __init__(self, app, limit=None, module=None):
        self._app_list = []
        if app:
            if not isinstance(app, list) and not isinstance(app, tuple):
                self._app_list.append(app)
            else:
                for item in app:
                    if item not in self._app_list:
                        if isinstance(item, _AppsFunc):
                            self._app_list.append(item)
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
                    self._app_list = list(
                        filter(lambda x: module in "%s_%s_%s" % (x._module.replace('.', '_'), x._name, x.number),
                               self._app_list))
                else:
                    self._app_list = app_func_list
        self._length = len(self._app_list)
        self._start = 0
        self._step = 1

    def __call__(self, *args, **kwargs):
        if self._app_list.__len__() == 1:
            return self._app_list[0](*args, **kwargs)
        elif self._app_list.__len__() < 1:
            return None
        else:
            raise IndexError("有多个应用请指定")

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._app_list[item]
        else:
            raise AttributeError(f'{str(self.__class__.__name__)} not have this attr')

    def __str__(self):
        return f'AppList({",".join(["%s_%s_%s" % (attr._module.replace(".", "_"), attr._name, attr._number) for attr in self._app_list])})'

    def __getattr__(self, item):
        if item in dir(self):
            raise AttributeError(f'{str(self.__class__.__name__)} not have this attr')
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


class _Park(object):
    """
    应用注册、应用继承的核心类， 记录模块自带已注册应用，每个注册都有编号，自定义注册将在这些已注册应用后
    """
    _register_number = 0
    _registered_number = []
    _exclude_func = ['install_module', 'make_dir_or_doc', 'render', 'start', 'encryption', '_CacheClass',
                     '_CurrencySetting', '_ProgressPark', '_SelfStart',
                     '_RealTimeUpdate', '_ParkConcurrency', 'ParkQueue', 'ReClass',
                     '_ComputerSystem', '_GPUClass', 'EncryptionData']

    def __init__(self, exclude=3, order='number', limit=None, *args, **kwargs):
        self._exclude_mode = exclude
        self._order_by = order
        self._limit = limit
        self._register_apps = {}
        self._register_funcs = {}

    def _register(self, func=None, call: bool = False, **kwarg):
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
                'number': self._register_number,
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
                self._register_apps[name + '_' + str(self._register_number)] = result
                self._register_number += 1
                self._registered_number.append(self._register_number)
            elif isfunction(func):
                self._register_funcs[name + '_' + str(self._register_number)] = result
                self._register_number += 1
                self._registered_number.append(self._register_number)

            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper
        else:
            def wrapper(func_call):
                is_call = call
                inherit_ = kwarg.get('inherit', False)
                func_arg = kwarg.get('arg', tuple())
                func_name = func_call.__name__
                if hasattr(func_call, '_name'):
                    func_name = func_call._name

                func_obj = None
                if is_call and func_arg:
                    if isinstance(func_arg, dict):
                        func_obj = func_call(**func_arg)
                    elif isinstance(func_arg, tuple) or isinstance(func_arg, list):
                        func_obj = func_call(*func_arg)
                    else:
                        func_obj = func_call(func_arg)
                elif is_call:
                    func_obj = func_call()
                func_result = {
                    'number': self._register_number,
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
                    self._register_apps[func_name + '_' + str(self._register_number)] = func_result
                    self._register_number += 1
                    self._registered_number.append(self._register_number)
                elif isfunction(func_call):
                    self._register_funcs[func_name + '_' + str(self._register_number)] = func_result
                    self._register_number += 1
                    self._registered_number.append(self._register_number)

                def warp(*args, **kwargs):
                    return func_obj(*args, **kwargs)

                return warp

            return wrapper

    def _inherit(self, **kwarg):
        def wrapper(func):
            parent = kwarg.get('parent', None)
            number = kwarg.get('number', None)
            warn = kwarg.get('warn', False)
            register_ = kwarg.get('register', True)
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
            app_arg = app._args
            call = app._obj
            app = app._app
            if not isclass(app):
                raise ValueError('(%s) 方法不支持继承函数使用该装饰器(inherit)' % func.__name__)

            if register_:
                arg = kwarg.get('args', None)
                obj, arg = self._inherit_func_inner(func, app, args=arg, app_arg=app_arg, call=call)
                self.register(obj, kwargs={
                    'call': True if arg else False,
                    'args': arg
                })

            def warp(*args, **kwargs):
                return self._inherit_func(func, app, args=(args, kwargs), app_arg=app_arg)

            return warp

        return wrapper

    def _inherit_func(self, func, app, args, app_arg, call=None):
        obj, arg = self._inherit_func_inner(func, app, args, app_arg, call=call)
        return _AppsFunc(obj, arg)

    def _inherit_func_inner(self, func, app, args, app_arg, call):
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
                if call:
                    self.app_init(app_args)
                self._sub_args = args
                if self._sub_args:
                    self.sub_init()

            def app_init(self, app_args):
                if app_args and isclass(app):
                    if app_args.__len__() == 2 and isinstance(app_args[0], tuple) and isinstance(app_args[1], dict):
                        self._parent_app = app(self, *app_args[0], **app_args[1])
                    elif isinstance(app_args, dict):
                        self._parent_app = app(self, **app_args)
                    elif not isinstance(app_args, str) and isinstance(app_args, Iterable):
                        self._parent_app = app(*app_args)
                    else:
                        self._parent_app = app(app_args)
                elif not app_args and isclass(app):
                    self._parent_app = app()
                elif isfunction(app):
                    self._parent_func[app.__name__] = app

            def sub_init(self):
                if self._sub_args and isclass(func):
                    if isinstance(self._sub_args, dict):
                        self._sub_app = func(**self._sub_args)
                    elif self._sub_args.__len__() == 2 and isinstance(self._sub_args[0], tuple) \
                            and isinstance(self._sub_args[1], dict):
                        self._sub_app = func(*self._sub_args[0], **self._sub_args[1])
                    elif not isinstance(self._sub_args, str) and isinstance(self._sub_args, Iterable):
                        self._sub_app = func(*self._sub_args)
                    else:
                        self._sub_app = func(self._sub_args)
                elif not self._sub_args and isclass(func):
                    self._sub_app = func()
                elif isfunction(func):
                    self._sub_func[func.__name__] = func

            def __getattr__(self, item):
                res = re.search('([a-zA-Z_]+?)__(sub|parent)$', item)
                if res and res.group(2) == 'sub':
                    if res.group(1) in dir(self._sub_app):
                        return eval(f'self._sub_app.{res.group(1)}')
                    else:
                        return self._sub_func[res.group(1)]
                elif res and res.group(2) == 'parent':
                    if res.group(1) in dir(self._sub_app):
                        return eval(f'self._parent_app.{res.group(1)}')
                    else:
                        return self._parent_func[res.group(1)]
                else:
                    for obj in parent_class:
                        try:
                            no1 = eval(f'super(obj, self).{item}')
                            if no1:
                                return no1
                        except AttributeError:
                            try:
                                return eval(f'obj.{item}')
                            except AttributeError:
                                continue
                    return None

            def __getitem__(self, item):
                if item in self.func:
                    return self.func[item]
                else:
                    super(NewClass, self).__getattr__(item)

            @classmethod
            def _generate_name(cls):
                cls._name = func.__name__

        NewClass._generate_name()

        return NewClass, {'app_args': app_arg if app_arg else {}}

    def _register_function(self, func=None, **kwarg):
        inherit_apps = []
        func_name = func.__name__
        if hasattr(func, '_name'):
            func_name = func._name
        func_kwargs = kwarg.get(func.__name__, {}) or kwarg.get(func_name, {})
        is_call = func_kwargs.get('call', False)
        func_arg = func_kwargs.get('args', tuple())
        if isinstance(func_arg, str) and self._func_dict['_data_source']:
            try:
                func_arg = eval(func_arg)
            except NameError:
                func_arg = func_arg
        register_mode = func_kwargs.get('mode', 0)
        if register_mode == 1:
            number = func_kwargs.get('number', None)
            inherit_app = self[func_kwargs.get('inherit', '')]
            if inherit_app.__len__() > 1 and not number:
                app = inherit_app[0]
            else:
                app = inherit_app
            if isinstance(number, int):
                app = self[inherit_app][number]
            app_arg = app._args
            if isinstance(app_arg, str) and self._func_dict['_data_source']:
                try:
                    app_arg = eval(app_arg)
                except NameError:
                    app_arg = app_arg
            app = app._app
            if not isclass(app):
                raise ValueError('(%s) 方法不支持继承函数使用该装饰器(inherit)' % func.__name__)

            inherit_apps.append(self._inherit_func(func=func, app=app, app_arg=app_arg, args=func_arg))
        else:
            func_obj = None
            if is_call and func_arg:
                if isinstance(func_arg, dict):
                    func_obj = func(**func_arg)
                elif isinstance(func_arg, tuple) or isinstance(func_arg, list):
                    func_obj = func(*func_arg)
                else:
                    func_obj = func(func_arg)
            elif is_call:
                func_obj = func()
            func_result = {
                'number': self._register_number,
                'func': func,
                'func_obj': func_obj,
                'args': func_arg,
                'info': {
                    'module': func.__module__ if func.__module__ != '__main__' else 'this',
                    'doc': func.__doc__,
                    'name': func.__name__,
                },
                'create_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'process': None,
            }
            if isclass(func):
                self._register_apps[func_name + '_' + str(self._register_number)] = func_result
                self._register_number += 1
                self._registered_number.append(self._register_number)
            elif isfunction(func):
                self._register_funcs[func_name + '_' + str(self._register_number)] = func_result
                self._register_number += 1
                self._registered_number.append(self._register_number)
        return inherit_apps

    def register(self, apps, kwargs=None):
        res = []
        if kwargs is None:
            kwargs = {}
        elif isinstance(kwargs, str):
            kwargs = self._load_json(kwargs)
            kwargs['_data_source'] = True
        if type(apps).__name__ == 'module':
            index_app = dir(apps).index('__builtins__')
            index_func = dir(apps).index('__spec__')
            funcs = dir(apps)[:index_app] + dir(apps)[index_func + 1:]
            for func in funcs:
                if type(eval(f'apps.{func}')).__name__ != 'module':
                    res += self._register_function(func=eval(f'apps.{func}'), **kwargs)
        else:
            if isinstance(apps, Iterable):
                if isinstance(apps, str):
                    raise
                else:
                    for app in apps:
                        if type(app).__name__ == 'module':
                            index_app = dir(app).index('__builtins__')
                            index_func = dir(app).index('__spec__')
                            funcs = dir(app)[:index_app] + dir(app)[index_func + 1:]
                            for func in funcs:
                                if type(eval(f'app.{func}')).__name__ != 'module':
                                    res += self._register_function(func=eval(f'app.{func}'), **kwargs)
                        elif isinstance(app, str):
                            raise
                        else:
                            res += self._register_function(func=app, **kwargs)
            else:
                func_name = apps.__name__
                if hasattr(apps, '_name'):
                    func_name = apps._name
                app_kw = kwargs.get(apps.__name__, {}) or kwargs.get(func_name, {})
                if not app_kw:
                    kwargs = {apps.__name__: kwargs}
                res += self._register_function(func=apps, **kwargs)
        return _AppList(res)

    def _get_exclude_list(self):
        func_keys = self._register_funcs.keys()
        app_keys = self._register_apps.keys()
        func_key = []
        app_key = []
        if self._exclude_mode == 1:
            for key_f in func_keys:
                key = re.search(r'(.*)_\d+', key_f).group(1)
                if key not in self._exclude_func:
                    func_key.append(key_f)
            for key_a in app_keys:
                key = re.search(r'(.*)_\d+', key_a).group(1)
                if key not in self._exclude_func:
                    app_key.append(key_a)
        elif self._exclude_mode == 2:
            for key_f in func_keys:
                key = re.search(r'(.*)_\d+', key_f).group(1)
                if key not in self._exclude_func:
                    func_key.append(key_f)
            for key_a in app_keys:
                key = re.search(r'(.*)_\d+', key_a).group(1)
                if key not in self._exclude_func:
                    app_key.append(key_a)
        else:
            func_key = list(func_keys)
            app_key = list(app_keys)
        return func_key, app_key

    def __getitem__(self, item):
        func_keys, app_keys = self._get_exclude_list()
        app_key_list = list(func_keys) + list(app_keys)
        sort_app_list = sorted(app_key_list, key=lambda x: x.split('_')[-1])
        if isinstance(item, str):
            it, *types = item.split('__') if '__' in item else (item, [''])
            kwargs = {}
            if '.' in it:
                its = copy.deepcopy(it)
                it = it.split('.')[-1]
                kwargs['module'] = its.replace('.', '_')

            def _get_app_name(key):
                pattern = re.compile(r'([a-zA-Z_]+)_\d+')
                name = re.search(pattern=pattern, string=key)
                if name:
                    return name.group(1)

            func_list = list(filter(lambda x: it == _get_app_name(x), func_keys))
            app_list = list(filter(lambda x: it == _get_app_name(x) or it in dir(self._register_apps[x]['func']),
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
                func = [_AppsFunc(self._register_funcs[key]) for key in sorted(func_list,
                                                                               key=lambda x: x.split('_')[1])]
            if app_list:
                apps = [_AppsFunc(self._register_apps[key]) for key in sorted(app_list,
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
                    return _AppList(app=res, **kwargs)
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
                    res = sorted(res, key=lambda x: x._number)
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
                return _AppList(app=res, **kwargs)

        elif isinstance(item, int):
            result = list(filter(lambda x: x.split('_')[-1] == str(item), sort_app_list))
            if result:
                if result[0] in func_keys:
                    return _AppList(app=_AppsFunc(self._register_funcs[result[0]]))
                elif result[0] in app_keys:
                    return _AppList(app=_AppsFunc(self._register_apps[result[0]]))
            else:
                return _AppList(app=_AppsFunc(self._register_apps.get(sort_app_list[item])
                                              or self._register_funcs.get(sort_app_list[item])))
            return _AppList(app=None)
        elif isinstance(item, slice):
            keys = sort_app_list[item]

            return _AppList(app=[_AppsFunc(self._register_apps.get(key)
                                           or self._register_funcs.get(key)) for key in keys])

    def __getattr__(self, item):
        order_mode = ''
        order_by = 'number'
        if self._order_by:
            order = re.split(r'\s+', self._order_by)
            order_by = order[0]
            if order.__len__() > 1:
                order_mode = order[1]
        func_keys, app_keys = self._get_exclude_list()
        func = [_AppsFunc(self._register_funcs[key]) for key in sorted(func_keys,
                                                                       key=lambda x: x.split('_')[1])]
        apps = [_AppsFunc(self._register_apps[key]) for key in sorted(app_keys,
                                                                      key=lambda x: x.split('_')[1])]
        if item in dir(self):
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
                res = sorted(res, key=lambda x: x._number)
            if order_mode.upper() == 'DESC':
                res = res[::-1]
            return _AppList(app=res)
        else:
            raise AttributeError(f'{str(self.__class__.__name__)} not have this attr')

    @property
    def app(self):
        return self.__getattr__('app')

    @property
    def apps(self):
        return self.__getattr__('apps')

    @property
    def func(self):
        return self.__getattr__('func')

    @property
    def all(self):
        return self.__getattr__('all')

    @property
    def funcs(self):
        return self.__getattr__('funcs')

    def __len__(self, key=None):
        func_list, app_list = self._get_exclude_list()
        if key == 'func':
            return len(func_list)
        elif key == 'app':
            return len(app_list)
        return len(app_list) + len(func_list)

    @staticmethod
    def _load_json(path):
        from ..conf.os import isExists
        if isExists(path=path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise FileNotFoundError('请提供正确的地址')


class _TaskProcess(_Park):
    _func_process_number = 0
    _func_dict = {}

    def _task(self, func, app=None, kwargs=None):
        args = kwargs.get('args', ())
        mode = kwargs.get('mode', 0)
        timing = kwargs.get('timing', None)
        item = func
        if app:
            item = f'{app}.{func}'
        for obj in self[item]:
            module = obj._module
            name = obj._name
            obj_kwargs = {}
            for key in [f'{module}.{name}', module, name]:
                if key in kwargs:
                    obj_kwargs = kwargs.get(key)
                    break
            function = eval(f"obj.{item.split('.')[-1]}")
            self._func_dict[str(self._func_process_number)] = {
                'func': function,
                'args': obj_kwargs.get('args', False) or args,
                'mode': obj_kwargs.get('mode', False) or mode,
                'timing': obj_kwargs.get('timing', False) or timing,
                'source': kwargs.get('_data_source', False)
            }
            self._func_process_number += 1

    def _wait(self):
        res = self._start()
        return res

    def _start(self):
        res = {}
        if self._func_dict:
            mode_0 = list(filter(lambda k: self._func_dict[k]['mode'] == 0 and not self._func_dict[k]['timing'],
                                 self._func_dict.keys()))
            timing = list(filter(lambda k: isinstance(self._func_dict[k]['timing'], datetime.datetime),
                                 self._func_dict.keys()))
            if mode_0:
                res['TASK_NOW'] = {}
                number = 0
                for key in mode_0:
                    number += 1
                    args = self._func_dict[key]['args']
                    if isinstance(args, str) and self._func_dict[key]['source']:
                        try:
                            args = eval(args)
                        except NameError:
                            args = args
                    name = self._func_dict[key]['func'].__name__
                    module = self._func_dict[key]['func'].__module__
                    res['TASK_NOW'][module + f'-{name}'] = {}
                    res['TASK_NOW'][module + f'-{name}']['execute_date'] = \
                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    if isinstance(args, dict):
                        res['TASK_NOW'][module + f'-{name}']['result'] = \
                            self._func_dict[key]['func'](**args)
                    elif isinstance(args, tuple) or isinstance(args, list):
                        res['TASK_NOW'][module + f'-{name}']['result'] = \
                            self._func_dict[key]['func'](*args)
                    else:
                        res['TASK_NOW'][module + f'-{name}']['result'] = \
                            self._func_dict[key]['func'](args)
            if timing:
                self._timing_func(timing=timing, _func_dict=self._func_dict)
            return res
        else:
            return True

    @staticmethod
    def _timing_func(timing, _func_dict):
        res = []
        func_dict = {}
        for key in timing:
            if _func_dict[key]['timing'] and isinstance(_func_dict[key]['timing'], datetime.datetime):
                time_key = _func_dict[key]['timing'].strftime('%Y-%m-%d %H:%M:%S')
                if time_key in func_dict.keys():
                    func_dict[_func_dict[key]['timing'].strftime('%Y-%m-%d %H:%M:%S')] += [key]
                else:
                    func_dict[_func_dict[key]['timing'].strftime('%Y-%m-%d %H:%M:%S')] = [key]
        while True:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            time_list = list(filter(lambda x: now > x, func_dict.keys()))
            if time_list.__len__() == func_dict.keys().__len__():
                break
            if now in func_dict.keys():
                for k in func_dict[now]:
                    func = _func_dict[k]['func']
                    args = _func_dict[k]['args']
                    if isinstance(args, str) and _func_dict[k]['source']:
                        try:
                            args = eval(args)
                        except NameError:
                            args = args
                    if isinstance(args, dict):
                        res.append(func(**args))

                    elif isinstance(args, list) or isinstance(args, tuple):
                        res.append(func(*args))
                    else:
                        res.append(func(args))
                    func_dict[now].remove(k)
        return res


class Park(_TaskProcess):
    EXCLUDE_SYS = 1
    EXCLUDE_SELF = 2
    EXCLUDE_DEFAULT = 3
    TASK_NOW = 0
    REGISTER = 0
    INHERIT = 1

    def __call__(self, exclude=3, order='number', limit=None, *args, **kwargs):
        self._exclude_mode = exclude
        self._order_by = order
        self._limit = limit
        return self

    def tasks(self, apps, kwargs=None):
        if kwargs is None:
            kwargs = {}
        elif isinstance(kwargs, str):
            kwargs = self._load_json(kwargs)
            kwargs['_data_source'] = 'file'
        if not isinstance(apps, str) and isinstance(apps, Iterable):
            for app in apps:
                name = app.split('.')
                func = name[-1]
                app = '.'.join(name[:-1])
                self._task(func=func, app=app, kwargs=kwargs)
        else:
            name = apps.split('.')
            func = name[-1]
            app = '.'.join(name[:-1])
            self._task(func=func, app=app, kwargs=kwargs)
        return self._wait()


park = Park()
registers = park.register
register = park._register
inherit = park._inherit
