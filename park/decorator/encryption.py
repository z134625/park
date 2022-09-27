import datetime
import hashlib
import re
import base64
from Crypto.Cipher import AES
from . import register


@register
class EncryptionData(object):

    def __init__(self, data, mode, timeout, key=None):
        assert type(data).__name__ in ['str', 'list', 'tuple', 'dict', 'set', 'int']
        str_data = str(data)
        self.str_data = str_data.encode('utf-8')
        self._timeout = timeout
        self._aes_key = (key or str(id(self)))
        if mode == 0:
            self._result = self._md5_data()
        elif mode == 1:
            self._result = self._sha1_data()
        elif mode == 2:
            self._result = self._base64_data()
        elif mode == 3:
            self._result = self._AES_data()
        self.mode = mode

    def _generate_data(self):
        datetime_pattern = re.compile(r'^(\d{4})-(\d{1,2})-(\d{1,2}) (\d{1,2}):?(\d{1,2}):?(\d{1,2})')
        date_pattern = re.compile(r'^(\d{4})-(\d{1,2})-(\d{1,2})')
        _timeout = None
        if self._timeout:
            if isinstance(self._timeout, int) or isinstance(self._timeout, float):
                now_time = datetime.datetime.now() + datetime.timedelta(minutes=self._timeout)
                _timeout = _timeout = {
                    'year': now_time.year,
                    'month': now_time.month,
                    'day': now_time.day,
                    'hour': now_time.hour,
                    'minute': now_time.minute,
                    'second': now_time.second,
                }
            elif isinstance(self._timeout, datetime.datetime):
                _timeout = {
                    'year': self._timeout.year,
                    'month': self._timeout.month,
                    'day': self._timeout.day,
                    'hour': self._timeout.hour,
                    'minute': self._timeout.minute,
                    'second': self._timeout.second,
                }
            elif isinstance(self._timeout, datetime.date):
                _timeout = {
                    'year': self._timeout.year,
                    'month': self._timeout.month,
                    'day': self._timeout.day + 1,
                    'hour': 0,
                    'minute': 0,
                    'second': 0,
                }
            elif isinstance(self._timeout, str):
                if re.search(datetime_pattern, self._timeout):
                    _time = datetime.datetime.strptime(self._timeout, '%Y-%m-%d %H:%M:%S')
                    _timeout = {
                        'year': _time.year,
                        'month': _time.month,
                        'day': _time.day,
                        'hour': _time.hour,
                        'minute': _time.minute,
                        'second': _time.second,
                    }
                elif re.search(date_pattern, self._timeout):
                    _time = datetime.datetime.strptime(self._timeout, '%Y-%m-%d')
                    _timeout = {
                        'year': _time.year,
                        'month': _time.month,
                        'day': _time.day + 1,
                        'hour': 0,
                        'minute': 0,
                        'second': 0,
                    }
        data = {
            'data': self.str_data,
            'timeout': _timeout,
        }
        return str(data).encode('utf-8')

    def _md5_data(self, data=None):
        return hashlib.md5(data or self._generate_data()).hexdigest()

    def _sha1_data(self, data=None):
        return hashlib.sha1(data or self._generate_data()).hexdigest()

    def _base64_data(self, data=None):
        return base64.b64encode(data or self._generate_data())

    @staticmethod
    def _add_to_16(message):
        while len(message) % 16 != 0:
            message = str(message)
            message += '\0'
        return message.encode('utf-8')

    def _AES_data(self):
        data = self._generate_data()
        aes = AES.new(self._add_to_16(self._aes_key), AES.MODE_ECB)
        message_16 = self._add_to_16(data)
        encrypt_aes = aes.encrypt(message_16)
        encrypt_aes_64 = base64.b64encode(encrypt_aes)
        return encrypt_aes_64

    def decrypt_data(self, data, mode=None, key=None, timeout_key=None):
        if mode or self.mode in [0, 1]:
            raise ValueError('md5 or sha1 不支持解密')
        elif mode or self.mode == 2:
            data_dict = eval(base64.b64decode(data).decode('utf-8'))
            return self._check_timeout_data(data_dict, timeout_key)
        elif mode or self.mode == 3:
            aes = AES.new(self._add_to_16(key or str(id(self))), AES.MODE_ECB)
            message_de64 = base64.b64decode(data)
            message_de64_data = aes.decrypt(message_de64)
            data_dict = eval(eval(message_de64_data.decode('utf-8').rstrip('\0')).decode('utf-8'))
            return self._check_timeout_data(data_dict, timeout_key)

    def _check_timeout_data(self, data_dict, timeout_key=None):
        if not data_dict.get('timeout'):
            return data_dict.get('data', b'').decode('utf-8')
        else:
            now_time = datetime.datetime.now()
            com_time = {
                'now_year': now_time.year,
                'now_month': now_time.month,
                'now_day': now_time.day,
                'now_hour': now_time.hour,
                'now_minute': now_time.minute,
                'now_second': now_time.second,
            }
            for res, com in zip(data_dict.get('timeout').keys(), com_time.keys()):
                if data_dict.get('timeout')[res] == com_time[com]:
                    continue
                elif data_dict.get('timeout')[res] > com_time[com]:
                    break
                elif data_dict.get('timeout')[res] < com_time[com]:
                    if not timeout_key:
                        raise TimeoutError('该数据已超时无法查看')
                    else:
                        if str(timeout_key) != str(id(self)):
                            raise KeyError("超时密钥错误, 无法查看")
            return eval(data_dict.get('data', b'').decode('utf-8'))

    @property
    def result(self):
        return self._result.decode()

    def __str__(self):
        return str(self._result.decode())


@register
def encryption(mode=2, timeout=None):
    def wrapper(func):
        def warp(*args, **kwargs):
            res = func(*args, **kwargs)
            return EncryptionData(data=res, mode=mode, timeout=timeout)
        return warp
    return wrapper

