import functools
import os
import re
import shutil
import sys
import warnings
import hashlib

from typing import Union, List, Any, Tuple, Iterable

LISTFILE = 0
LISTDIR = 1
LISTALL = 2
pwd_mode = 'md5'
v_project = [
]


def warning(msg: str, warn: bool = True,
            _type: warnings = RuntimeWarning,
            level: int = 2) -> None:
    """
    警告方法，
    """
    if warn:
        warnings.warn(msg, _type, stacklevel=level)
    return


def mkdir(path: str, exist: bool = True) -> bool:
    """
    创建文件夹
    """
    dir_: str = path
    try:
        os.mkdir(dir_)
    except FileExistsError:
        return False
    except FileNotFoundError:
        os.makedirs(dir_, exist)
    finally:
        return True


def remove(path: str, file=True, warn=True) -> bool:
    """删除文件"""

    def _tree_file(_p: str):
        for _f in listPath(_p, splicing=True, mode=LISTFILE, list=False):
            try:
                os.remove(_f)
            except FileNotFoundError:
                continue
        for _d in listPath(_p, splicing=True, mode=LISTDIR, list=False):
            _tree_file(_d)

    try:
        os.remove(path)
        return True
    except PermissionError:
        if file:
            _tree_file(path)
            return True
        shutil.rmtree(path)
        return True
    except FileNotFoundError:
        warning(f"该文件或文件夹({path})不存在或已删除", warn=warn)
        return False


def listPath(path: str, mode: int = LISTFILE, **kwargs) -> Union[list, map, filter]:
    """
    列出路径下的所有文件
    :param path: 路径
    :param mode: 模式
    :param kwargs: 支持使用where进行条件筛选， where 传入参数应为一种函数或者方法，需要的则应返回True， 不需要的返回False
    :return : 一组文件名
    """
    doc: bool = False
    dir_: bool = False
    if mode == 0:
        doc: bool = True
    elif mode == 1:
        dir_: bool = True
    like: str = kwargs.get("like", None)
    suffix: list = kwargs.get('suffix', [])
    suffix = list(map(lambda x: x.upper(), suffix))
    list_: bool = kwargs.get("list", True)
    splicing: bool = kwargs.get("splicing", False)
    files: List[str] = list(filter(lambda x: not x.startswith('.'), os.listdir(path)))
    if doc:
        files: filter = filter(lambda x: os.path.isfile(os.path.join(path, x)), files)
    if dir_:
        files: filter = filter(lambda x: os.path.isdir(os.path.join(path, x)) if not x.startswith('.') else False,
                               files)
    if suffix:
        files: filter = filter(lambda x: os.path.splitext(x)[1][1:].upper() in suffix, files)
    if like:
        files: filter = filter(lambda x: like in x, files)
    if splicing:
        files: map = map(lambda x: os.path.join(path, x), files)
    if list_:
        files: List[str] = list(files)
    return files


def update_attrs_dict(
        name: str,
        K: dict,
        attrs: dict
) -> dict:
    """
    用于更新属性中字典，避免同名覆盖
    例如:
    attrs = {'a': {'b': 1}}
    K = {'a': {'c': 1}}
    attrs.update(K) -> {'a': {'c': 1}}
    update_attrs_dict('a', K, attrs) -> {'a': {'c': 1, 'b': 1}}
    """
    if name in attrs:
        attrs[name].update(K)
    else:
        attrs[name] = K
    return attrs


def update_changeable_var(
        old: dict,
        new: dict,
        var=None
):
    """
    该方法用于 对var中的键 做出可变修改
    与update_attrs_dict一致
    """
    if var is None:
        var = []
    for v in var:
        update_attrs_dict(v, old.get(v, {}), new)
        if v in old:
            old.pop(v)
    new.update(old)


@functools.lru_cache()
def formatSize(bytes_: Union[float, int]):
    """
    :param bytes_: 数据字节数
    :return:  返回数据字节转化大小， kb, M, G
    _formatSize(1024)
    '1.000KB'
    _formatSize(1024 * 1024)
    '1.000M'
    _formatSize(1000)
    '0.977KB'
    _formatSize("fs")
    传入的字节格式不对
    'Error'
    """
    try:
        bytes_ = float(bytes_)
        kb = bytes_ / 1024
    except ValueError:
        print("传入的字节格式不对")
        return "Error"

    if kb >= 1024:
        M = kb / 1024
        if M >= 1024:
            G = M / 1024
            return "%.3fG" % G
        else:
            return "%.3fM" % M
    else:
        return "%.3fKB" % kb


def get_size(item):
    def _get_size(obj, seen=None):
        size = sys.getsizeof(obj)
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        seen.add(obj_id)
        if isinstance(obj, dict):
            size += sum([_get_size(v, seen) for v in obj.values()])
            size += sum([_get_size(k, seen) for k in obj.keys()])
        elif hasattr(obj, '__dict__'):
            size += _get_size(obj.__dict__, seen)
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum([_get_size(i, seen) for i in obj])
        return size

    return formatSize(_get_size(item))


@functools.lru_cache()
def readPy(file: str) -> dict:
    """
    file 为 字符串
    将py格式的字符串中的变量生成字典形式返回
    """
    exec(file)
    return locals()


def setAttrs(obj: Any, self: bool = False, cover: bool = True, warn: bool = True, **kwargs) -> Any:
    """
    对传入的obj 对象设置属性， 必须保证该对象有paras 属性，并且paras为Paras
    对于有paras 属性的 对象， 可在paras 设置属性 _cover 以及 _warn 来限制是否弹出警告 是否覆盖属性内容
    对于非paras 的对象 可在添加参数cover warn 默认都为True 设置的属性 增加函数参数即可
    即： setAttrs(obj, _cover=True, _warn=False
    对应的 这将对obj 对象设置 _cover _warn 两个参数
    设置的属性为 _set_dict 中的字典数据  调用方式
    obj.key = value
    self 参数在复制一个对象时， 会重复设置属性此时 为True避免重复警告  默认为False
    """
    if hasattr(obj, 'paras') and hasattr(obj.paras, 'PARK_PARAS') and getattr(obj.paras, 'PARK_PARAS'):
        cover: bool = True
        warn: bool = True
        for key, value in obj.paras.SET_LIST:
            root = obj.paras.ROOT
            if not root:
                obj.paras.ROOT = True
            has: bool = key in dir(obj)
            if not root:
                obj.paras.ROOT = False
            if not has:
                setattr(obj, key, value)
            else:
                warning("当前设置重复的属性(%s)，将覆盖该属性" % key,
                        warn=(warn and obj.paras.WARN) and (cover and obj.paras.COVER) and not self)
                if cover and obj.paras.COVER:
                    setattr(obj, key, value)
            if obj.paras.ROOT:
                d: dict = {key: eval(f'obj.{key}')}
            else:
                obj.paras.ROOT = True
                d: dict = {key: eval(f'obj.{key}')}
                obj.paras._root = False
            obj.paras.ATTRS.update(d)
        obj.paras.SET_LIST.clear()
    elif kwargs:
        for key, value in kwargs.items():
            warning("当前设置重复的属性(%s)，将覆盖该属性" % key, warn=warn and cover)
            if cover:
                setattr(obj, key, value)
    return obj


def args_tools(args: Any, self=None) -> Tuple[tuple, dict]:
    if callable(args) and self:
        args = args(self)
    if isinstance(args, (tuple, list)):
        args = (args, {})
    elif isinstance(args, dict):
        args = ((), args)
    elif args is not None:
        args = ((args,), {})
    else:
        args = ((), {})
    return args


class _Context(dict):

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError:
            return self.__getattr__(item)

    def __getattr__(self, item):
        if item in self:
            return self[item]
        raise AttributeError(f'属性错误, 没有该属性{item}')


def length(s, **kwargs):
    if kwargs.get('max', 999) >= len(s) >= kwargs.get('min', 0):
        return True
    else:
        if len(s) < kwargs.get('min', 0):
            raise ValueError('密码过短')
        if len(s) > kwargs.get('max', 0):
            raise ValueError('密码过长')


def types(s, **kwargs):
    pattern1 = re.compile(r'[a-z]')
    pattern2 = re.compile(r'[A-Z]')
    pattern3 = re.compile(r'[0-9]')
    pattern4 = re.compile(r'[^0-9a-zA-Z]')
    error = []
    if kwargs.get('a_z') and not re.search(pattern1, s):
        error.append('密码必须包含字母')
    if kwargs.get('A_Z') and not re.search(pattern2, s):
        error.append('密码必须包含大写字母')
    if kwargs.get('number') and not re.search(pattern3, s):
        error.append('密码必须包含数字')
    if kwargs.get('sign') and not re.search(pattern4, s):
        error.append('密码必须包含特殊符号')
    if error:
        raise ValueError('\n'.join(error))
    return True


def hard(s, **kwargs):
    return True


def _password_check(_PWD, _project=None):
    projects = _project
    if not projects:
        projects = v_project
    error = []
    for v_p in projects:
        try:
            eval(v_p.get('func'))(_PWD, **v_p.get('kwargs'))
        except Exception as e:
            error.append(str(e))
    if error:
        raise ValueError('\n'.join(error))
    return True


# @functools.lru_cache()
def get_password(pwd: str, reversal=False, _project=None):
    if _password_check(pwd, _project):
        if pwd_mode == 'md5':
            m = hashlib.md5()
            m.update(pwd.encode())
        elif pwd_mode == 'sha1':
            m = hashlib.sha1()
            m.update(pwd.encode())
        pwd = m.hexdigest()
    return pwd


def verification_pwd(_O, _N):
    a = get_password(_N)
    if a == _O:
        return True
    else:
        return False


def _generate_name(
        name: str,
        names: Iterable,
        mode: int = 0,
        dif: bool = False,
        suffix: bool = '',
) -> str:
    if mode == 1:
        name, suffix = os.path.splitext(name)
        names = list(
            map(lambda x: os.path.splitext(x)[0], filter(lambda x: os.path.splitext(x)[1] == suffix, names)))
    if name in names:
        start = ' (1)'
        pattern_number = re.compile(r'.* \((\d+)\)')
        pattern_letter = re.compile(r'.* \(([A-Z]+)\)')
        pattern = pattern_number
        if dif:
            start = ' (A)'
            pattern = pattern_letter
        number = re.match(pattern=pattern, string=name)
        if number:
            number = number.group(1)
            if not dif:
                new_name = re.sub(r'\(\d+\)$', '(%d)' % (int(number) + 1), name)
            else:
                if not number.endswith('Z'):
                    new_name = re.sub(r'\([A-Z]+\)$', '(%s)' % (number[:-1] + chr(ord(number[-1]) + 1)), name)
                else:
                    new_name = re.sub(r'\([A-Z]+\)$', '(%s)' % (number + 'A'), name)
        else:
            new_name = name + start
        if new_name in names:
            return _generate_name(new_name, names, mode=0, dif=dif, suffix=suffix)
        return new_name + suffix
    return name + suffix


def exists_rename(
        path: str,
        paths: List[str] = None,
        clear: bool = False,
        dif: bool = False) -> str:
    if not clear:
        if os.path.isdir(path):
            if path.endswith('/'):
                path = path[:-1]
            names = listPath(path=os.path.dirname(path), splicing=False, list=True)
            return os.path.join(os.path.dirname(path), _generate_name(name=os.path.basename(path),
                                                                      names=names, dif=dif))
        if os.path.isfile(path):
            names = listPath(path=os.path.dirname(path), splicing=False, list=True)
            return os.path.join(os.path.dirname(path), _generate_name(name=os.path.basename(path),
                                                                      names=names, mode=1, dif=dif))
        else:
            names = []
            if paths:
                names = paths
            return _generate_name(name=path, names=names, dif=dif)
    else:
        name, suffix = os.path.splitext(path)
        pattern = re.compile(r'(.*) \([0-9]+\)')
        res = re.search(pattern=pattern, string=name)
        if res:
            name_head = res.group(1)
            return name_head + suffix
        else:
            return path


def number_to_chinese(
        amount: Union[int, float, str]
) -> str:
    c_dict = {1: u'', 2: u'拾', 3: u'佰', 4: u'仟'}
    x_dict = {1: u'元', 2: u'万', 3: u'亿', 4: u'兆'}
    g_dict = {0: u'零', 1: u'壹', 2: u'贰', 3: u'叁', 4: u'肆', 5: u'伍', 6: u'陆', 7: '柒', 8: '捌', 9: '玖'}

    def number_split(number):
        g = len(number) % 4
        number_list = []
        lx = len(number) - 1
        if g > 0:
            number_list.append(number[0:g])
        k = g
        while k <= lx:
            number_list.append(number[k:k + 4])
            k += 4
        return number_list

    def number_to_capital(number):
        len_number = len(number)
        j = len_number
        big_num = ''
        for i in range(len_number):
            if number[i] == '-':
                big_num += '负'
            elif int(number[i]) == 0:
                if i < len_number - 1:
                    if int(number[i + 1]) != 0:
                        big_num += g_dict[int(number[i])]
            else:
                big_num += g_dict[int(number[i])] + c_dict[j]
            j -= 1
        return big_num

    number = str(amount).split('.')
    integer_part = number[0]
    chinese = ''
    integer_part_list = number_split(integer_part)
    integer_len = len(integer_part_list)
    for i in range(integer_len):
        if number_to_capital(integer_part_list[i]) == '':
            chinese += number_to_capital(integer_part_list[i])
        else:
            chinese += number_to_capital(integer_part_list[i]) + x_dict[integer_len - i]
    if chinese and '元' not in chinese:
        chinese += '元'
    if chinese and len(number) == 1:
        chinese += '整'
    else:
        fractional_part = number[1]
        fractional_len = len(fractional_part)
        if fractional_len == 1:
            if int(fractional_part[0]) == 0:
                chinese += '整'
            else:
                chinese += g_dict[int(fractional_part[0])] + '角整'
        else:
            if int(fractional_part[0]) == 0 and int(fractional_part[1]) != 0:
                chinese += '零' + g_dict[int(fractional_part[1])] + '分'
            elif int(fractional_part[0]) == 0 and int(fractional_part[1]) == 0:
                chinese += '整'
            elif int(fractional_part[0]) != 0 and int(fractional_part[1]) != 0:
                chinese += g_dict[int(fractional_part[0])] + '角' + g_dict[int(fractional_part[1])] + '分'
            else:
                chinese += g_dict[int(fractional_part[0])] + '角整'
    return chinese
