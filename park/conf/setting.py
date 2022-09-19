import re
import os
import sys
import time
import uuid
import warnings
import json
import copy
import datetime
import inspect
import logging
import configparser
import _queue
import psutil

from multiprocessing import Process, Queue, Pipe
from typing import List, Any, Type
from collections.abc import Iterable
from ..sql.mysql.dict_generator import dict_sql
from ._error import *
from .os import (
    _path_join,
    _remove,
    _get_size,
    _split_path,
    _list_path,
    _is_dir,
    _is_exists,
    _base_name,
    _path_abs,
    _dir_name,
    _mkdir_path,
)
from ..decorator import register, inherit, park

__all__ = (
    'CurrencySetting',
    'ProgressPark',
    'TrainProgressPark',
    'setting',
    'Cache',
    'Time',
    'Date',
    'Stamp',
    "Command",
    "SelfStart",
    "RealTimeUpdate",
    "ParkConcurrency",
    "ParkQueue",
    "PythonPath",
    "PythonVersion",
    "CachePath",
    "install_module",
    "make_dir_or_doc"
)

_NOW_TIME = datetime.datetime.now()
_NOW_TIME_FORMAT = _NOW_TIME.strftime('%Y-%m-%d %H:%M:%S')
_NOW = f'{_NOW_TIME.year}-{_NOW_TIME.month}-{_NOW_TIME.day}'
_STAMP = time.time
_python_path = _dir_name(sys.executable)
_python_version = sys.version
_cache_path = _path_join(_python_path, "Lib\\site-packages\\park\\cache")

_command = sys.argv


@register(call=True)
class _CacheClass:
    """
    缓存删除工具，直接调用即可， class_：可以传入字符串，列表，以及路径， all_ 默认为False ，
    若传入字符串将在缓存路径中查找该类的内容， 若列表则查找列表中类的内容， 若传入路径则会以当前路径为基点进行删除操作
    all_若为True 则表示该该类下所有内容都将删除，无法恢复！谨慎使用
    name 表示指定删除文件名包括拓展名， 若all_开启则该项目无效
    like 传入字符串，为要删除文件的包含的名，若包含将全部删除
    """
    _res_file = []

    def __init__(self):
        self.path = None

    def __call__(self, class_: str | List[str] = None, all_: bool = False, name: str | list | tuple = None,
                 **kwargs):
        if isinstance(class_, list):
            for item in class_:
                self._delete(item, all_, name, **kwargs)
        else:
            self._delete(class_, all_, name, **kwargs)
        return self

    def _delete(self, cla, all_, name, **kwargs) -> None:
        res = False
        if _is_exists(cla) and not _is_dir(cla):
            self.path = _path_join(_cache_path, f'{cla}')
        if cla is None:
            self.path = _cache_path
        else:
            self.path = cla
        if all_:
            yes = "y"
            if not kwargs.get("ignore_warning", False):
                yes = input(f"\033[1;31;31m 本次操作将删除{self.path}下所有内容，是否继续操作?(y/n)\033[0m")
            if yes == "y" or yes == "yes":
                if _remove(self.path):
                    res = True
        elif not all_ and name:
            if isinstance(name, Iterable) and not isinstance(name, str):
                name = list(name)
                for i in name:
                    if _remove(_path_join(self.path, i)):
                        res = True
                    else:
                        name.remove(i)
                        self._res_file.append(_path_join(self.path, i))
                name = ','.join(name)
            else:
                res = _remove(_path_join(self.path, name))
        elif kwargs.get("like", None):
            names = kwargs.get("like")
            for file in filter(lambda x: names in x, _list_path(self.path)):
                if _remove(_path_join(self.path, file)):
                    res = True
                else:
                    self._res_file.append(_path_join(self.path, file))
        else:
            raise SettingError("未提供删除文件名， 也不允许全部删除， 请修改配置")
        if res and self._res_file != []:
            print(f"\033[1;32;32m 删除成功({cla if cla else 'cache'}{',' + name if name else ''})\033[0m")

    @property
    def error(self):
        return self._res_file

    def remove_error(self):
        pass


@register(call=False)
class _CurrencySetting:
    log = logging

    def __init__(self):
        self.set_dict: dict = {}
        self.suffix_ini: list = ['.ini', '.cfg', '.conf']
        self.path = None
        self.suffix = None

    def init(self):
        self.set_dict: dict = {}
        self.suffix_ini: list = ['.ini', '.cfg', '.conf']
        self.path = None
        self.suffix = None

    def load(self, path: str, **kwargs):
        """加载配置文件, 支持ini、json、py、txt"""
        self.init()
        self.path: str = path
        _, suffix = _split_path(self.path)
        self.suffix: str = suffix.lower()
        if self.suffix == '.py':
            with open(self.path, 'r', encoding=kwargs.get("encoding", None)) as f:
                file = f.read()
                self.set_dict = {**self.set_dict, **self._readPy(file)}
        elif self.suffix == '.json':
            with open(self.path, 'r', encoding=kwargs.get("encoding", None)) as f:
                self.set_dict = {**self.set_dict, **json.load(f)}
                f.close()
        elif self.suffix in self.suffix_ini:
            config = configparser.ConfigParser()
            config.read(path, encoding='utf-8')
            d = {}
            for item in config:
                if config.has_section(item):
                    d[item] = dict(config.items(item))
            self.set_dict = {**self.set_dict, **d}
        elif self.suffix == 'txt':
            d = {}
            with open(self.path, 'r', encoding=kwargs.get("encoding", None)) as f:
                lines = f.readlines()
            for line in lines:
                try:
                    key, value = line.split("=")
                    d[key] = value
                except Exception as e:
                    print(f"({line})该行配置错误({e})")
                    continue
            self.set_dict = {**self.set_dict, **d}
        else:
            raise SettingError(f"暂不支持该格式({suffix})配置文件")
        return self(**kwargs)

    def __getitem__(self, item):
        return self._getValue(item)

    def __setitem__(self, key, value):
        self.set_dict[key] = value

    def __delitem__(self, key):
        del self.set_dict[key]

    def __getattr__(self, item):
        return self._getValue(item)

    def _getValue(self, item, delete: bool = False):
        key = []
        append = key.append

        def get_json(dict_):
            if isinstance(dict_, dict):
                if item in dict_:
                    if delete:
                        return dict_.pop(item)
                    return dict_[item]
                for j in dict_:
                    if isinstance(dict_[j], dict):
                        append(j)
                        result = get_json(dict_[j])
                        if result:
                            return result
            else:
                return None

        val = get_json(self.set_dict)
        append(item)
        from ..utils.data import SettingData
        return SettingData(key, val)

    def __call__(self, *args, **kwargs):
        if kwargs.get("log", False):
            from ..utils.log import Log
            self.log = Log(**kwargs)
        return self

    @staticmethod
    def _readPy(file):
        exec(file)
        return locals()

    @property
    def size(self):
        """返回配置文件的大小"""
        return _get_size(self.path)


@inherit(parent='_CurrencySetting')
class _Configs:
    delete = {

    }

    def __init__(self):
        """
        继承于通用配置类CurrencySetting，
        初始化其中一部分配置，通过加载配置文件的方法更新配置
        """
        super().__init__()

    @staticmethod
    def _load_global():
        """
        用于加载包中自带的全局变量
        :return:
        """
        from . import _Global_setting
        _Global_setting = _Global_setting
        default = ['__builtins__', '__cached__', '__doc__',
                   '__file__', '__loader__', '__name__', '__package__', '__spec__']
        global_settings = filter(lambda x: x not in default, dir(_Global_setting))
        d = {}
        for i in global_settings:
            d[i] = eval(f"_Global_setting.{i}")
        return d

    def __call__(self, *args, **kwargs):
        """
        提供加载全局配置， 删除全局配置
        删除配置时仅删除， 默认全局配置， 若新加载的配置覆盖它且参数变化将不再删除
        支持delete__keyword 删除配置文件中keyword的选项
        :param kwargs:  支持global_setting, delete_global参数
        :return: 配置
        """
        global_dict = self._load_global()
        if kwargs.get("global_setting", False):
            self.set_dict = global_dict
        if kwargs.get("delete_global", False):
            for key in global_dict:
                if key in self.set_dict and self.set_dict[key] == global_dict[key]:
                    self.set_dict.pop(key)
        pattern = re.compile(r'delete__([\w\d]+)')
        delete_keywords = filter(lambda x: re.match(pattern, x), kwargs.keys())
        for keyword in delete_keywords:
            keyword = re.match(pattern, keyword).group(1)
            if self[keyword]:
                self.delete[keyword] = self._getValue(keyword, delete=True)
        if kwargs.get("log", False):
            from ..utils.log import Log
            self.log = Log(**kwargs)
        return self


@register(call=False)
class _ProgressPark:
    """进度条实现
    with ProgressPark(len) as park():
    """

    def __init__(self, length: int):
        self.start = _STAMP()
        self.length = length
        self.epoch = 0

    @staticmethod
    def park(msg: str):
        sys.stdout.write(msg)
        sys.stdout.flush()

    def __call__(self, msg: str = None, start_msg: str = "Downloading.", end_msg: str = "Successfully",
                 error_msg: str = "Download Error", *args, **kwargs):
        self.epoch += 1
        self.progress = int((self.epoch + 1) / self.length * 100)

        func = kwargs.get("func", None)
        if func:
            print(f"{self.epoch}." + start_msg + '\r', end="", flush=True)
            sys.stdout.flush()
            try:
                func()
                print(f"{self.epoch}." + end_msg)
            except Exception as e:
                logging.error(e)
                print(error_msg)
        else:
            if msg:
                print(msg)
        sys.stdout.write("处理中:[%d%%]\r" % self.progress)
        sys.stdout.flush()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        """
            程序退出，将计算本次迭代所花费时间
        """
        self.end = _STAMP()
        sys.stdout.write(f"\033[1;32;32m处理完成[100%]\033[0m\n")
        sys.stdout.write("处理耗时:{}\n".format(self.end + 0.1 - 0.1 - self.start))


@inherit(parent='_ProgressPark')
class TrainProgressPark:
    batch = 0
    _execute = 0
    _finish = 0
    _total = 0
    _speed = 0

    def __init__(self, length: int):
        super(TrainProgressPark, self).__init__(length)
        self.gpu = park['GPU']

    def layer_epoch(self):
        """
        显示当前迭代次数，以及总共迭代次数, 调用方式
        for epoch in range(epochs):
            park.layer_epoch()
            ....
        显示方式：
            当前正迭代第1次，总共n次
        注意：
            放入位置应为开始迭代位置，即在训练数据之前，最好紧在训练数据前，保证其计算速度正确
        """
        self.epoch += 1
        print(f"\n当前正迭代第{self.epoch}次，总共{self.length}次")
        self.batch = 0
        self._total = 0
        self._execute = _STAMP()

    def layer_batch(self, length: int, **kwargs):
        """
        遍历数据进度显示，将显示用时用法：
        for i, data in enumerate(batch_data, 0):
            .....
            park.layer_batch(len(batch_data), run_loss=run_loss, total_loss=total_loss)
        显示方式：
            [>------------]1/len(batch_data) - (time) s 当前 loss=0.01
        当本次迭代完成将显示：
            [>>>>>>>>>>>>>]len(batch_data)/len(batch_data) - (avg_time) s 本次迭代平均 loss=0.01
        length 必选
         run_loss
                   > 可选, 若不填则显示为0， 时间计算将正常进行
         total_loss
        注意：
            应该放在最后即得到loss之后
        """
        self.batch += 1
        length = length
        progress = int((self.batch / length) * 30)
        over = 30 - progress
        progress_str = f"{self.batch} / {length}"
        self._finish = _STAMP()
        self._speed = self._finish + 0.1 - 0.1 - self._execute
        self._total += self._speed
        print("\r", end="")
        print("[%s]%s -(%.2f) s GPU占用率(%s / %s) GPU温度(%s) 当前 loss=%.8f" % (
        ('>' * progress + '-' * over), progress_str,
        self._speed, self.gpu[0]["Used"],
        self.gpu[0]["Memory"], self.gpu[0]["Temp"],
        kwargs.get('run_loss', 0))
              if self.batch != length else
              "[%s]%s -(%.2f) s GPU占用率(%s / %s) GPU温度(%s) 本次迭代平均 loss=%.8f" % (('>' * 30),
                                                                                          progress_str,
                                                                                          (self._total / self.batch),
                                                                                          self.gpu[0]["Used"],
                                                                                          self.gpu[0]["Memory"],
                                                                                          self.gpu[0]["Temp"],
                                                                                          (kwargs.get('total_loss',
                                                                                                      0) / self.batch)),
              end="")
        sys.stdout.flush()
        self._execute = _STAMP()

    def __exit__(self, *args, **kwargs):
        """
        程序退出，将计算本次迭代所花费时间
        """
        self.end = _STAMP()
        sys.stdout.write(f"\033[1;32;32m\n处理完成[100%]\033[0m\n")
        sys.stdout.write("处理耗时:{}\n".format(self.end + 0.1 - 0.1 - self.start))


@register(call=True)
class _SelfStart:
    _order = '%s\ncd %s\n%s %s'
    _hide_terminal = '@echo off\nif "%1" == "h" goto begin\n' \
                     + 'mshta vbscript:createobject("wscript.shell").run("""%~0"" h",0)(window.close)&&exit\n' \
                     + ':begin\n'
    _user = sys.executable
    _program = _base_name(_command[0])
    _cwd = _dir_name(_path_abs(_command[0]))
    _path = None

    def __init__(self):
        """
        初始化参数，获取当前操作系统，目前仅支持windows操作系统
        """
        system = os.name
        if system == 'posix':
            pass
        elif system == 'nt':
            self.bat_path = 'C:\\Users\\%s\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup' \
                            % os.getlogin()
            self._order = \
                self._order % (self._cwd[0:2], self._cwd, self._user, self._program)
        elif system == 'java':
            pass
        else:
            raise SystemError("暂不支持此系统")

    def __call__(self, *args, **kwargs):
        name: str = kwargs.get("name", self._program.split('.')[0])
        hide_terminal: bool = kwargs.get("hide_terminal", False)
        formal_parameter: str = kwargs.get("formal_parameter", None)
        if formal_parameter and isinstance(formal_parameter, str):
            self._order += formal_parameter
        if hide_terminal:
            self._order = self._hide_terminal + self._order
        self._write_file(name)
        return self

    def _write_file(self, name: str) -> None:
        name = name + '.bat'
        path = _path_join(self.bat_path, name)
        self._path = path
        if _is_exists(path):
            with open(self._path, "r") as f:
                order = f.read()
                f.close()
            if order == self._order:
                return
        with open(self._path, "w") as f:
            f.write(self._order)
            f.close()

    def close(self) -> bool:
        if self._path:
            return _remove(self._path)
        return False


@register
class _RealTimeUpdate:
    _parent_process_pid = None
    _children_process_pid = None
    start_process = None
    start_time = None
    add_parameter = False

    def __init__(self, func: Any = None, class_: Any = None, *args, **kwargs):
        """
        初始化参数
        :param func:
        :param args:
        :param kwargs:
        """
        self.func: Any = func
        self.class_ = class_
        self.args: tuple = args
        self.kwargs: dict = kwargs
        self._analysis()

    def parent(self) -> None:
        """

        :return:
        """
        self._parent_process_pid = os.getpid()
        path = os.getcwd()
        p1 = Process(target=self.children, args=self.args, kwargs=self.kwargs)
        p1.start()
        self._children_process_pid = p1.pid
        while True:
            if (self.start_time.second - datetime.datetime.now().second) % self.flush_time == 0:
                n = 0
                if os.stat(path).st_mtime > self.start_process and self._children_process_pid and n == 0:
                    p1.kill()
                    try:
                        psutil.Process(self._children_process_pid)
                    except psutil.NoSuchProcess:
                        print("loading....")
                        p1 = Process(target=self.children, args=self.args, kwargs=self.kwargs)
                        p1.start()
                        self._children_process_pid = p1.pid
                        self.start_process = time.time()
                        n += 1

    def children(self, *args, **kwargs) -> None:
        """
        :param args:
        :param kwargs:
        :return:
        """
        if self.func:
            self.func(*args, **kwargs)
        if self.class_:
            cls = self.class_(*args, **kwargs)
            if self.start_up:
                if self.call and not self.add_parameter:
                    self.start_up += '()'
                eval("cls.%s" % self.start_up)
        return

    def start(self) -> None:
        """

        :return:
        """
        try:
            self.start_process = time.time()
            self.start_time = datetime.datetime.now()
            self.parent()
        except KeyboardInterrupt:
            print("主动停止进程")

    def _analysis(self) -> None:
        """
        :return:
        """
        assert self.func or self.class_, "参数错误"
        self.flush_time: int = self.kwargs.get("flush", 3)
        self.start_up: str = self.kwargs.get("start_up", None)
        self.call: str = self.kwargs.get("call", True)
        kwargs = copy.deepcopy(self.kwargs)
        keys = kwargs.keys()
        if "flush" in keys:
            kwargs.pop("flush")
        if "start_up" in keys:
            kwargs.pop("start_up")
        if "call" in keys:
            kwargs.pop("call")
        self.kwargs = kwargs

    def parameter(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        self.add_parameter = True
        dict_analysis = re.sub(r'[`\'\s]', '', dict_sql(kwargs))
        dict_analysis = re.sub(r'and', ',', dict_analysis)
        tuple_analysis = str(list(args))
        tuple_analysis = re.sub(r'[\[\]]', '', tuple_analysis)
        if self.start_up:
            self.start_up += '(%s, %s)' % (tuple_analysis, dict_analysis)
        return self


@register(call=True)
class _ParkConcurrency:
    processList: List[Process] = []
    startProcess: List[Process] = []
    processPid: dict = {}
    pid: list = []
    queue: Type[Queue] | Queue = None
    pipe1: Pipe = None
    pipe2: Pipe = None

    def __init__(self):
        self._append_Process = self.processList.append
        self._Process_length = self.processList.__len__()
        self._pid_append = self.pid.append

    def addProcess(self, func: Any, *args, **kwargs):
        """
        :param func:
        :param args:
        :param kwargs:
        :return:
        """
        p = Process(target=func, args=args, kwargs=kwargs)
        if self.startProcess.__len__() < 20:
            self._append_Process(p)
        else:
            raise IOError("此方法不能添加过多的进程")

    # def __call__(self, *args, **kwargs):
    #     is_queue: bool = kwargs.get("queue", False)
    #     is_pipe: List[str] = kwargs.get("pipe", None)
    #     if is_queue:
    #         self.queue = Queue
    #         return self.send, self.recv
    #     elif is_pipe and is_pipe.__len__() == 2:
    #         self.pipe1, self.pipe2 = Pipe()

    def __getitem__(self, item):
        """
        :param item:
        :return:
        """
        if isinstance(item, slice):
            start = item.start
            stop = item.stop
            step = item.step
            self.startProcess = self.processList[item]
            return self
        elif isinstance(item, str):
            pattern = re.compile(r"[pP](\d+)")
            _id = re.match(pattern=pattern, string=item)
            if _id:
                _id = int(_id.group(1)) - 1
                return self.processList[_id]
            else:
                return None
        elif item is None:
            return None

    def start(self):
        """

        :return:
        """
        if not self.startProcess:
            self.startProcess = self.processList
        for i, process in enumerate(self.startProcess):
            process.start()
            self._pid_append(process.pid)
            self.processPid[process.pid] = process
        for process in self.startProcess:
            process.join()


@register
class ParkQueue:
    cache_path = _path_join(_cache_path, "queue")
    cache_data = _path_join(cache_path, f"{_NOW}-queue.json")

    def __init__(self, path: str = None):
        """

        :param path:
        """
        self.queue = Queue()
        self.pid = []
        self.key = None
        self.save_path = None
        if path:
            self.save_path = path

    def _send(self, queue: Any, msg: Any, sender: Any = None, recipient: str = None):
        """
        :param queue:
        :param msg:
        :param sender:
        :param recipient:
        :return:
        """
        try:
            self.key = self._make_key(sender, recipient)
            msg = {
                recipient: {"sender": sender,
                            "recipient": recipient,
                            "msg": msg,
                            "key": self.key,
                            },
            }
            queue.put(msg)
        except Exception as e:
            logging.error(f"{sender}发送信息失败({e})")
            warnings.warn(f"{sender}发送信息失败({e})", RuntimeWarning, stacklevel=2)

    def send(self, msg, recv: str = None):
        """

        :param msg:
        :param recv:
        :return:
        """
        f_name = inspect.getframeinfo(inspect.currentframe().f_back)[2]
        self._send(self.queue, msg, sender=f_name, recipient=recv)

    def recv(self, timeout: int = 5, pid: int = None):
        """

        :param timeout:
        :param pid:
        :return:
        """
        f_name = inspect.getframeinfo(inspect.currentframe().f_back)[2]
        msg = self._recv(self.queue, pid=pid, f_name=f_name)
        if msg:
            return msg
        else:
            for i in range(timeout):
                time.sleep(1)
                print("\r", end="")
                print(f"{os.getpid()}({f_name}):第{i + 1}次获取消息中....", end="")
                msg = self._recv(self.queue, pid=pid, f_name=f_name)
                if msg:
                    print("\n")
                    return msg
            print("\n")
            return None

    def set(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        if "pid" in kwargs:
            for val in kwargs.get("pid"):
                self.pid.append(val)

    def _recv(self, queue: Any, pid: Any = os.getpid, f_name: str = None):
        """

        :param queue:
        :param pid:
        :param f_name:
        :return:
        """
        try:
            infos = queue.get(timeout=1)
        except _queue.Empty:
            infos = {}
        self.queue_info = self._save_data(infos)
        if pid:
            pass
        else:
            try:
                if f_name in self.queue_info:
                    info = self.queue_info[f_name]
                    if self._check_key(info.get("key", ""), info.get("sender", ""), f_name):
                        return info
            except _queue.Empty:
                return None

    @staticmethod
    def _make_key(sender: str, recipient: str):
        """

        :param sender:
        :param recipient:
        :return:
        """
        sender_key = uuid.uuid5(uuid.NAMESPACE_URL, sender).hex
        recipient_key = uuid.uuid5(uuid.NAMESPACE_URL, recipient).hex
        key = "%s->%s" % (sender_key, recipient_key)
        key = uuid.uuid5(uuid.NAMESPACE_DNS, key)
        return key.hex

    def _check_key(self, key: str, sender: str, recipient: str, **kwargs):
        """

        :param key:
        :param sender:
        :param recipient:
        :param kwargs:
        :return:
        """
        sender = sender
        recipient = recipient
        return self._make_key(sender, recipient) == key

    def _save_data(self, msg: dict):
        """

        :param msg:
        :return:
        """
        data = {}
        new_data = msg
        if self.save_path:
            pass
        else:
            cache_path = _path_join(self.cache_path)
            if not _is_exists(self.cache_data) or not _is_exists(cache_path):
                _mkdir_path(cache_path)
                f = open(self.cache_data, "w")
                f.close()
            with open(self.cache_data, "r", encoding="gbk") as f:
                f_data = f.read()
                if f_data:
                    data = json.loads(f_data)
            with open(self.cache_data, "w", encoding="gbk") as f:
                new_data = {**new_data, **data}
                json_data = json.dumps(new_data)
                f.write(json_data)
            f.close()
        return new_data

    def del_cache(self):
        """

        :return:
        """
        _remove(self.cache_data)


@register
class ReClass:
    def __init__(self):
        self.pattern = re.compile
        self.result = None

    def __call__(self, *args, **kwargs):
        self.pattern = self.pattern(kwargs.get("pattern"))


@register
def install_module(module: str, install: str = None) -> int:
    try:
        __import__(module)
        return 0
    except ImportError:
        if not install:
            install = module
        print("Installing %s" % install)
        choice = input("Proceed (Y/n)?")
        if choice.upper() == 'Y':
            python_path = os.path.join(_python_path, "python.exe")
            stat = os.system(f"{python_path} -m pip install {install}")
            return stat
        else:
            raise ImportError("没有安装module 无法正常使用该模块")


@register
def make_dir_or_doc(path: str, suffix: str = None) -> None:
    basename = _base_name(path=path)
    if suffix and suffix in basename:
        _mkdir_path(path=_dir_name(path=path))
    else:
        _mkdir_path(path=path)


CurrencySetting = park['_CurrencySetting']
ProgressPark = park['_ProgressPark']
TrainProgressPark = TrainProgressPark
setting: _Configs = _Configs()
Cache = park['_CacheClass']
SelfStart = park['_SelfStart']
RealTimeUpdate = park['_RealTimeUpdate']
ParkConcurrency = park['_ParkConcurrency']

Time = _NOW_TIME_FORMAT
Date = _NOW
Stamp = _STAMP
PythonPath = _python_path
PythonVersion = _python_version
CachePath = _cache_path
Command = _command

