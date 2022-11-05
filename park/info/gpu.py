from typing import Any


class GPUClass:
    """
    查看电脑GPU 属性 self.gpu_count 显示电脑GPU数量，
    self.gpu 将返回cpu字符串， [0] 表示选择第一个GPU
    使用self.DriverVersion 或 self.version 将显示显卡驱动的版本信息
    self.gpu[0]["Memory"] 将显示第一个gpu的显存 (self.gpu[0]["显存"])
    self.gpu[0]["Used"] 将显示第一个gpu的已使用显存 (self.gpu[0]["已使用显存"])
    self.gpu[0]["Free"] 将显示第一个gpu的剩余显存 (self.gpu[0]["空余显存"])
    self.gpu[0]["Temp"] 将显示第一个gpu的温度 (self.gpu[0]["温度"])
    self.gpu[0]["Speed"] 将显示第一个gpu的风速 (self.gpu[0]["风速"])
    self.gpu[0]["Power"] 将显示第一个gpu的电源 (self.gpu[0]["电源"])
    """
    _name = 'park.gpu'
    __slots__ = ["gpu_count", "gpu", "DriverVersion", "version", "pynvml"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pynvml = __import__("pynvml")
        print(self.pynvml)
        try:
            self.pynvml.nvmlInit()
            self.gpu_count = self.pynvml.nvmlDeviceGetCount()
        except self.pynvml.nvml.NVMLError_LibraryNotFound or self.pynvml.nvml.NVMLError_Uninitialized:
            print('NVML Shared Library Not Found, GPU该功能将无法使用')

    def __getattr__(self, item):
        if item.lower() == 'gpu':
            return self
        elif item == "DriverVersion" or item == "version":
            return self.pynvml.nvmlSystemGetDriverVersion()
        else:
            return "没有该属性，请尝试(gpu(gpu名称)， version(驱动版本))"

    def __getitem__(self, item):
        if isinstance(item, int):
            handle = self.pynvml.nvmlDeviceGetHandleByIndex(item)
            return self.Info(handle, self.pynvml)

    def __str__(self):
        return "GPU"

    class Info:
        __slots__ = ["handle", "info", "pynvml"]

        def __init__(self, handle: Any, pynvml: Any):
            self.pynvml = pynvml
            self.handle = handle
            self.info = self.pynvml.nvmlDeviceGetMemoryInfo(self.handle)

        def __str__(self):
            return self.pynvml.nvmlDeviceGetName(self.handle)

        def __getitem__(self, item):
            if item.title() == "Memory" or item == "显存":
                return "%.3f G" % (self.info.total / 1024 / 1024 / 1024)

            elif item.title() == "Used" or item == "已使用显存":
                return "%.3f G" % (self.info.used / 1024 / 1024 / 1024)

            elif item.title() == "Free" or item == "空余显存":
                return "%.3f G" % (self.info.free / 1024 / 1024 / 1024)

            elif item.title() == "Temp" or item == "温度":
                return "%.2f C" % self.pynvml.nvmlDeviceGetTemperature(self.handle, 0)

            elif item.title() == "Speed" or item == "风速":
                return self.pynvml.nvmlDeviceGetFanSpeed(self.handle)

            elif item.title() == "Power" or item == "电源":
                return self.pynvml.nvmlDeviceGetPowerState(self.handle)

            else:
                return "没有该属性请尝试查看(Memory显存, Used已使用显存, Free空余显存, Temp温度, Speed风速, Power电源)"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pynvml.nvmlShutdown()

