
from typing import Any


class _ComputerSystem:
    __slots__ = ["info", "platform"]

    def __init__(self):
        self.platform = __import__("platform")
        self.info = self.platform.uname()

    def __str__(self):
        return self.info.system

    def __getattr__(self, item):
        if item == "node":
            return self.info.node

        elif item == "machine":
            return self.info.machine

        elif item == "processor":
            return self.info.processor

        elif item == "system":
            return self._System(self.platform, self.info.system)

        else:
            return "没有该属性，(请尝试node(网络名称), machine(计算机类型), processor(处理器信息), system(操作系统))"

    class _System:
        def __init__(self, plat: Any, system: str):
            self._plat = plat
            self._system = system

        def __str__(self):
            return self._system

        def __getitem__(self, item):
            if item == "version":
                return self._plat.version()

            elif item == "architecture":
                return self._plat.architecture()

            elif item == "complete":
                return self._plat.platform()

            else:
                return "没有该内容，请尝试(version(操作系统版本), architecture(操作系统位数), complete(操作系统名称及版本号))"


SYS = _ComputerSystem


__all__ = ("SYS", )
