import json
from typing import Any, Iterable, List, Union, Tuple, TextIO, Set

from ..tools import _Context


class _Paras:
    """
    配置基础类
    仅显示公有变量属性
    """
    BAN: List[str] = []

    @staticmethod
    def init() -> dict:
        # 增加的配置
        ...

    def update(self,
               kwargs: dict,
               sel: bool = False,
               is_obj: bool = False
               ) -> Any:
        """
        更新配置的一些属性
        """
        ...

    def inherit_update(self, _O):
        ...


class _ParkLY:
    """
    模型基础类
    仅显示公有变量属性
    """
    __bases__ = (object,)
    __new_attrs__: Set[str]
    paras: _Paras

    @property
    def context(self) -> _Context: ...

    def exists_rename(
            self,
            path: str,
            paths: List[str] = None,
            clear: bool = False,
            dif: bool = False
    ) -> str: ...

    @property
    def flags(self) -> _Context: ...

    def generate_name(
            self,
            name: str,
            names: Iterable,
            mode: int = 0,
            dif: bool = False,
            suffix: bool = '',
    ) -> str: ...

    def get(
            self,
            content: dict
    ): ...

    def init(self,
             **kwargs
             ) -> None:
        ...

    def load(self,
             key: Union[str, None] = None,
             args: Union[Tuple[Tuple[Any], dict], dict, List, Tuple, None] = None
             ) -> Any:
        ...

    def open(self,
             file: str,
             mode: str = 'r',
             encoding: Union[None, str] = 'utf-8',
             lines: bool = False,
             datas: Any = None,
             get_file: bool = False
             ) -> Union[TextIO, None, Any]:
        ...

    def save(self,
             key: Union[str, None] = None,
             args: Union[Tuple[Any], None] = None
             ) -> None:
        ...

    def sudo(self,
             gl: bool = False
             ) -> Any:
        ...

    def update(self,
               K: dict = None
               ) -> Union[Any]:
        ...

    def with_context(self,
                     context: dict = None,
                     gl: bool = False
                     ) -> Any:
        ...

    def with_paras(self,
                   gl: bool = False,
                   **kwargs
                   ) -> Any:
        ...

    def with_root(self,
                  gl: bool = False
                  ) -> Any:
        ...

    @property
    def is_save_log(self) -> bool:
        ...

    @property
    def save_path(self) -> str:
        ...

    @property
    def save_suffix(self) -> dict:
        ...

    @property
    def save_io(self) -> list:
        ...

    @property
    def save_mode(self) -> str:
        ...

    @property
    def save_encoding(self) -> str:
        ...

    @property
    def speed_info(self) -> dict:
        ...

    @property
    def test_info(self) -> dict:
        ...


JsonType = type(json.dumps({}))
