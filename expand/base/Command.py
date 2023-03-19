import sys
import re
import time
from typing import (
    Tuple,
    Callable,
    Any,
    Iterable,
    Union,
    List,
    Dict
)
from types import (
    FunctionType,
    MethodType
)

from .paras import CommandParas
from ...utils import api
from ...utils.base import ParkLY
from ...utils.env import env


class _ParkProgress(object):

    def __init__(
            self,
            epoch_show: bool,
            enum: bool,
            ext: Union[None, List[str], Tuple[str]] = None
    ):
        self.epoch_show = epoch_show
        self.ext = ext
        self.enum = enum

    def __call__(
            self,
            obj: Iterable,
            start: int = 0,
            step: int = 1
    ):
        self.obj = [item for item in obj]
        self._start = start
        self._step = step
        self._length = len(self.obj)
        self._epoch = 0
        return self

    def __iter__(
            self
    ):
        return self

    def __next__(
            self
    ):
        self._start += self._step
        if self._start > self._length:
            raise StopIteration
        else:
            res = self.obj[self._start - self._step]
            if self.enum:
                res = (self._start - self._step, self.obj[self._start - 1])
            return res

    def bar(
            self,
            msgs: Union[str, None] = None
    ) -> Callable[[Any, Iterable], None]:
        def warp(
                func: Union[FunctionType, MethodType],
                items: Iterable
        ) -> None:
            total = len(list(items))
            ext = self.ext * total
            for i, item in enumerate(items):
                if callable(func):
                    func(item)
                now = int((i + 1) / total * 50)
                this = msgs % f' {ext[i]} [{">" * now + "-" * (50 - now)}]({round((i + 1) / total * 100, 2)}%)'
                print(this, end='', flush=True)

        return warp

    def epoch(
            self,
            msg: Union[str, None] = None,
            typ: bool = True,
            start: bool = False
    ) -> str:
        log = env.log.debug
        if not start:
            msgs = f"\033[1;32;32m\r当前迭代第{self._epoch}，{msg or '....'} %s\033[0m\n"
            if not typ:
                log = env.log.error
                msgs = f"\033[1;31;31m\r当前迭代第{self._epoch}，{msg or '....'} %s\033[0m\n"
            log(f"""当前迭代第{self._epoch}，{msg or '....'}""")
        else:
            self._epoch += 1
            msgs = f"\033[1;31;31m\r当前正迭代第{self._epoch}个中....%s\033[0m"
        if self.epoch_show:
            print(msgs % '', end='', flush=True)
        return msgs

    def epochs(
            self,
            func: Union[FunctionType, MethodType],
            name: str = None,
            args: Any = None,
            error: Union[str, None] = None,
            success: Union[str, None] = None,
            bar: bool = False
    ) -> Tuple[bool, str]:
        try:
            msgs = self.epoch(start=True)
            kw = {}
            if bar:
                kw = {
                    'bar': self.bar(msgs)
                }
            if isinstance(args, (tuple, list)):
                if len(args) == 2 and isinstance(args[0], tuple) and isinstance(args[0], dict):
                    res = func(*args[0], **{**args[1], **kw})
                else:
                    res = func(*args, **kw)
            elif args:
                res = func(args, **kw)
            else:
                res = func(**kw)
            res = True, res
        except Exception as e:
            res = False, str(e)
        r = '成功' if res[0] else '失败'
        msg = success if res[0] else error
        if callable(msg):
            msg = msg(res[1])
        self.epoch(msg=msg or
                       f"该程序({name or (func.__name__ if hasattr(func, '__name__') else str(func))})执行{r}",
                   typ=res[0])
        return res

    @staticmethod
    def success(
            msg: Union[str, None] = None
    ) -> None:
        msgs = '\n' + (msg or '成功！')
        env.log.debug(msgs)
        print(msgs)

    @staticmethod
    def error(
            msg: Union[str, None] = None
    ) -> None:
        msgs = '\n' + (msg or '失败！')
        env.log.error(msgs)
        print(msgs)

    def __enter__(
            self
    ):
        return self

    def __exit__(
            self,
            exc_type,
            exc_val,
            exc_tb
    ):
        self._epoch = 0
        del self


class Command(ParkLY):
    _name = 'command'
    paras = CommandParas()

    def __getattribute__(self, item):
        res = super().__getattribute__(item)
        if 'command_flag' in dir(res):
            return self._command_flag(res)
        return res

    def _command_flag(
            self,
            res: Union[Any]
    ) -> Callable[[Tuple[Any], Dict[str, Any]], Any]:
        if hasattr(res, 'command_flag'):
            return self._command(res, **res.command_flag)
        return res

    def _command(
            self,
            func: Union[FunctionType, MethodType],
            keyword: Union[str, List[str], Tuple[str]],
            name: str,
            unique: bool = False,
            priority: int = -1
    ) -> Callable[[Tuple[Any], Dict[str, Any]], Any]:
        """
        装饰器 用于封装， 命令启动程序
        配置类command 装饰器使用
        """
        if isinstance(keyword, str):
            self.context.command_keyword[keyword] = keyword + '$'
            self.context.command_info[keyword + '$'] = {
                'help': func.__doc__ or '没有使用帮助',
                'func': func.__name__,
                'unique': unique,
                'priority': priority,
                'name': name,
            }
        elif isinstance(keyword, (tuple, list)):
            keyword = sorted(keyword)
            keyword.reverse()
            keys = '$'.join(keyword)
            for key in keyword:
                self.context.command_keyword[key] = keys + '$'
            self.context.command_info[keys + '$'] = {
                'help': func.__doc__ or '没有使用帮助',
                'func': func.__name__,
                'unique': unique,
                'priority': priority,
                'name': name
            }

        def command_warps(
                *args,
                **kwargs
        ) -> Union[Any]:
            res = func(*args, **kwargs)
            return res

        setattr(command_warps, '__func__', func)
        return command_warps

    def progress(
            self,
            enum: bool = True,
            epoch_show: bool = True
    ) -> _ParkProgress:
        return _ParkProgress(
            epoch_show=epoch_show,
            enum=enum,
            ext=self.context.ext_bar
        )

    @api.command(
        keyword=['--help'],
        name='help'
    )
    def help(
            self,
            order: str = None
    ) -> None:
        """
        此操作将打印每种方法的帮助信息
        """
        if not order:
            keyword = self.context.command_keyword
            keys = set(map(lambda x: keyword[x], keyword.keys()))
            for key in sorted(keys):
                strs = key.replace('$', '\t')
                print(f"""{strs}: \n {self.context.command_info[key]['help']}""")
        else:
            if order in self.context.command_info:
                print(f"""{order}: \n {self.context.command_info[order]['help']}""")
            else:
                print(f"""{order}: \n 没有该帮助， 请检查""")

    def _re_commands(
            self,
            S: str
    ) -> None:
        res = re.match(r'(--[a-zA-Z0-9-_]+)=(\S+)', S)
        if res:
            if res.group(1) in self.context.command_keyword:
                info = self.context.command_info[self.context.command_keyword[res.group(1)]]
                self.context.command_k_2_args.update({
                    res.group(1): {
                        'func': info['func'],
                        'args': res.group(2),
                        'priority': info['priority'],
                        'unique': info['unique'],
                        'name': info['name'],
                    }
                })
                self.context.command_k_true.append(S)

    def main(
            self,
            _commands: Union[List[str], Tuple[str], None] = None,
            delay: Union[int, None] = None,
            epoch_show: bool = True
    ) -> None:
        """
        命令行启动主程序
        """
        commands = sys.argv[1:]
        if _commands:
            commands = _commands + commands
        error = []
        command_keyword = self.context.command_keyword
        list(map(lambda s: self._re_commands(s), commands))
        cs = list(filter(lambda x: x in command_keyword, commands))
        for c in cs:
            index = commands.index(c) + 1
            args = None
            if index < len(commands) and \
                    commands[index] not in command_keyword and \
                    commands[index] not in self.context.command_k_true:
                args = commands[index]
            info = self.context.command_info[command_keyword[c]]
            self.context.command_k_2_args.update({
                c: {
                    'func': info['func'],
                    'args': args,
                    'priority': info['priority'],
                    'unique': info['unique'],
                    'name': info['name'],
                }
            })
        commands = list(self.context.command_k_2_args.items())
        commands.sort(key=lambda x: x[1]['priority'])
        with self.progress(enum=False, epoch_show=epoch_show) as pg:
            for keys, info in pg(commands):
                if '-h' in commands or '--help' in commands:
                    if '-h' in commands:
                        index = commands.index('-h') + 1
                    else:
                        index = commands.index('--help') + 1
                    if index < len(commands) and commands[index]:
                        args = (commands[index],)
                    self.help(*args)
                    break
                args = info['args'] and (info['args'],)
                if info['unique'] and keys in commands[commands.index((keys, info)):]:
                    raise IOError("当前指令(%s)只允许执行一次" % keys)
                func = info['func']
                func = eval(f'self.{func}')
                res = pg.epochs(func=func, name=info['name'], args=args)
                if not res[0]:
                    error.append(res[1])
                if delay:
                    time.sleep(delay)
            if not error:
                return pg.success()
            else:
                return pg.error(msg='\n'.join(error))
        self.main_clear()

    def main_clear(
            self
    ) -> None:
        """
        用于清除本次main程序启动时增加的缓存变量
        """
        self.command_k_2_args.clear()
        self.command_k_true.clear()
