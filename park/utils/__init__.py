import re
import warnings
from collections.abc import Iterable

from inspect import isclass, isfunction


class _Park(object):
    _register_number = 0
    _register_apps = {}
    _register_funcs = {}

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
                    'module': func.__module__,
                    'doc': func.__doc__,
                    'name': func.__name__,
                }
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

            return wrapper
        else:
            def wrapper(func_call):
                is_call = call
                func_arg = kwarg.get('arg', None)
                queue_task = kwarg.get('task', False)
                func_name = func_call.__name__
                if hasattr(func_call, '_name'):
                    func_name = func_call._name

                func_obj = tuple()
                if not queue_task:
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
                            'module': func_call.__module__,
                            'doc': func_call.__doc__,
                            'name': func_call.__name__,
                        },
                        'process': None,
                    }
                else:
                    func_result = {

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
                            super(NewClass, self).__getattr__(item)

                    def __getitem__(self, item):
                        if item in self.func:
                            return self.func[item]
                        else:
                            super(NewClass, self).__getattr__(item)

                return NewClass(app_args=(self, *app_arg) if app_arg else (self,))

            return warp

        return wrapper

    def __getitem__(self, item):
        it, types = item.split('__') if '__' in item else (item, None)
        func_list = list(filter(lambda x: it in x, self._register_funcs.keys()))
        app_list = list(filter(lambda x: it in x or it in dir(self._register_apps[x]['func']),
                               self._register_apps.keys()))
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
                return self._AppList(app=func + apps)
            else:
                raise ImportError('(%s)该类或方法还未注册' % item)
        else:
            if types == 'app':
                return self._AppList(app=apps)
            elif types == 'func':
                return self._AppList(app=func)
            else:
                return self._AppList(app=[])

    class _AppsFunc:
        def __init__(self, obj: dict):
            self.app = obj['func']
            self.obj = obj['func_obj']
            self.args = obj['args']
            self.info = obj['info']
            self.number = obj['number']
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

        def __init__(self, app):
            self._app_list = []
            if not isinstance(app, Iterable):
                self._app_list.append(app)
            else:
                for item in app:
                    if item not in self._app_list:
                        self._app_list.append(item)
            self._app_list.sort(key=lambda x: x.number)
            self._length = len(self._app_list)
            self._start = 0
            self._step = 1

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
