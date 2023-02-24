import json
from typing import Any, Iterable, List, Union, Tuple, TextIO, Set

from ..tools import _Context


class _Paras:
    """
    配置基础类
    仅显示公有变量属性
    """
    ban: List[str] = []

    @staticmethod
    def init() -> dict:
        # 增加的配置
        pass

    def update(self,
               kwargs: dict,
               sel: bool = False,
               is_obj: bool = False
               ) -> Any:
        """
        更新配置的一些属性
        """
        pass


class _ParkLY:
    """
    模型基础类
    仅显示公有变量属性
    """
    __bases__ = (object, )
    __new_attrs__: Set[str]
    paras: _Paras

    @property
    def context(self) -> _Context:
        return self.context

    def exists_rename(self,
                      path: str,
                      paths: List[str] = None,
                      clear: bool = False,
                      dif: bool = False) -> str:
        pass

    @property
    def flags(self) -> _Context:
        return self.flags

    def generate_name(self,
                      name: str,
                      names: Iterable,
                      mode: int = 0,
                      dif: bool = False,
                      suffix: bool = '',
                      ) -> str:
        pass

    def get(self, content: dict):
        pass

    def init(self,
             **kwargs
             ) -> None:
        pass

    def load(self,
             key: Union[str, None] = None,
             args: Union[Tuple[Tuple[Any], dict], dict, List, Tuple, None] = None
             ) -> Any:
        pass

    def open(self,
             file: str,
             mode: str = 'r',
             encoding: Union[None, str] = 'utf-8',
             lines: bool = False,
             datas: Any = None,
             get_file: bool = False
             ) -> Union[TextIO, None, Any]:
        pass

    def save(self,
             key: Union[str, None] = None,
             args: Union[Tuple[Any], None] = None
             ) -> None:
        pass

    def sudo(self,
             gl: bool = False
             ) -> Any:
        pass

    def update(self,
               K: dict = None
               ) -> Union[Any]:
        pass

    def with_context(self,
                     context: dict = None,
                     gl: bool = False
                     ) -> Any:
        pass

    def with_paras(self,
                   gl: bool = False,
                   **kwargs
                   ) -> Any:
        pass

    def with_root(self,
                  gl: bool = False
                  ) -> Any:
        pass

    @property
    def is_save_log(self) -> bool:
        return self.is_save_log

    @property
    def save_path(self) -> str:
        return self.save_path

    @property
    def save_suffix(self) -> dict:
        return self.save_suffix

    @property
    def save_io(self) -> list:
        return self.save_io

    @property
    def save_mode(self) -> str:
        return self.save_mode

    @property
    def save_encoding(self) -> str:
        return self.save_encoding

    @property
    def speed_info(self) -> dict:
        return self.speed_info

    @property
    def test_info(self) -> dict:
        return self.test_info


JsonType = type(json.dumps({}))
