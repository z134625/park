import logging

from ...conf.os import (
    BASE_PATH,
    join,
    absPath,
    isExists,
    mkdir,
    remove,
)


__all__ = ("Log", )
__doc__ = """
'log', :    log = log(setting, format_=None) 
            log(msg, class_="error")
            日志查看删除 log.cat_delete(is_save: bool = False, save_path: str = BASE_PATH,
                 time_: str = NOW, delete: bool = False, all_: bool = False)
                 is_save 将导出日志 根据save_path 导出 time_默认导出现在时间,
                 delete开启将删除time_ 指定的日志,all_ 开启将删除所有日志
"""


class _LogClass:
    log_info = ""

    def __init__(self, **kwargs):
        from ...conf.setting import Date
        format_: str = '\n文件路径:%(pathname)s 程序:%(filename)s 函数:%(funcName)s 位置:%(lineno)s' \
                       f'\n 信息:%(message)s \n 时间:%(asctime)s\n {"-" * 20} \n'
        if kwargs.get("format", None):
            format_ = kwargs.get("format", None)
        from ...conf.setting import setting
        level = eval(f"logging.{setting.level.value.upper() if setting.level.value else 'DEBUG'}")
        LOG_DIR: str = setting.log_path.value if setting.log_path.value \
            else join(absPath(BASE_PATH), 'cache/log')
        if not isExists(LOG_DIR):
            mkdir(LOG_DIR)
        filename = join(LOG_DIR, f'{Date}.log')
        datefmt = setting.datefmt.value if setting.datefmt.value else '%a %d %b %Y %H:%M:%S'
        filemode = 'a'
        set_dict = {
            "level": level,
            "filename": filename,
            "datefmt": datefmt,
            "filemode": filemode,
            "format": format_,
        }
        logging.basicConfig(**set_dict)
        self.LOG_DIR = LOG_DIR

    def cat_delete(self, is_save: bool = False, save_path: str = BASE_PATH,
                   time_: str = None, delete: bool = False, all_: bool = False):
        from ...conf.setting import Date
        time_ = time_ if time_ else Date
        with open(join(self.LOG_DIR, f'{time_}.log'), 'r') as f:
            log_list = f.readlines()
        if is_save:
            with open(join(save_path, time_), 'w') as f:
                for item in log_list:
                    f.write(item)
        self.log_info = ''.join(log_list)
        if all_ and delete:
            remove(self.LOG_DIR)
        elif delete:
            try:
                remove(join(self.LOG_DIR, f'{time_}.log'))
            except FileNotFoundError as e:
                raise e

    def __str__(self):
        return self.log_info

    def __call__(self, msg: str, *args, **kwargs) -> None:
        class_ = kwargs.get("class_", "debug").lower()
        eval(f"logging.{class_}('{msg}')")


Log = _LogClass



