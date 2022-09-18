
import logging
import warnings
from typing import Any


class TorchModule:
    from ..conf.setting import Time, Date
    from ..conf import Error
    from ..utils.data import SettingData
    Time = Time
    Date = Date
    Error = Error
    _lr = 0.0001
    _momentum = 0.9
    _optim = "Adam"
    _optimizer = None
    path_to = None
    _ModuleDict = None
    _loss = None
    _X = None
    _T = None
    LossFunc = None
    _SetTing = {
        "is_gpu": SettingData("is_gpu", True),
        "loss": SettingData("loss", "M"),
        "lr": SettingData("lr", _lr),
        "momentum": SettingData("momentum", _momentum),
        "optim": SettingData("optim", _optim),
        "model_name": SettingData("model_name", "model"),
        "model_path": SettingData("model_path", "cache/model"),
    }

    def __init__(self, version: bool = True, conf: bool = True):
        """
        初始化pytorch模块提供优化器，保存模型，加载模型等模块
        """
        from ..utils.data import Compare, VersionCompare
        from ..conf.setting import setting
        self.torch = __import__("torch")

        t_v = VersionCompare(self.torch.__version__)
        if version:
            print("当前torch版本为 %s" % t_v)
        res_compare = Compare(t_v, VersionCompare("1.9.0"))
        if ">=" not in res_compare:
            warnings.warn("当前torch版本低于要求版本(1.9.0)，可能会有未知错误", RuntimeWarning, stacklevel=2)
        self.nn = self.torch.nn
        self.optim = self.torch.optim
        if conf:
            self.setting = setting
        else:
            self.setting = self._SetTing
        self.device = self.torch.device("cuda"
                                        if self.torch.cuda.is_available() and self.setting["is_gpu"].value
                                        else "cpu")
        logging.debug(f"当前使用{self.device}")
        self.device_count = self.torch.cuda.device_count()
        self.DataParallel = self.nn.DataParallel
        self.np_tensor = self.torch.from_numpy
        self.Tensor = self.torch.Tensor

    def loss(self, loss: str = None) -> Any:
        """
        创建损失函数
        根据配置文件内容进行选择损失函数， 默认为M 即均方差
        包含的损失函数有：
        1. M 均方差
        2. A 平均绝对误差
        3. E 交叉熵
        4. C 时间分类
        5. N 负对数似然
        6. P 目标泊松分布
        7. G 高斯负对数似然
        8. B 二元交叉熵
        选择合适的损失函数后，可直接进行调用即：
        Loss(outputs, target)
        Loss = loss(loss="m")
        """

        time_ = self.Time
        idea = self.setting["loss"].value.upper() if self.setting["loss"].value else "M"
        if loss:
            idea = loss.upper()
        if idea == 'M':
            """均方差"""
            logging.debug(f"{time_}-选择的损失函数方法为:均方差")
            loss_ = self._mean_squared_error()
        elif idea == 'A':
            """平均绝对误差"""
            logging.debug(f"{time_}-选择的损失函数方法为:平均绝对误差")
            loss_ = self._mean_abs_error()
        elif idea == 'E':
            """交叉熵损失"""
            logging.debug(f"{time_}-选择的损失函数方法为:交叉熵损失")
            loss_ = self._cross_entropy_error()
        elif idea == 'C':
            """时间分类损失"""
            logging.debug(f"{time_}-选择的损失函数方法为:时间分类损失")
            loss_ = self._ctc_error()
        elif idea == 'N':
            """负对数似然损失"""
            logging.debug(f"{time_}-选择的损失函数为:负对数似然损失")
            loss_ = self._nll_error()
        elif idea == 'P':
            """目标泊松分布的负对数似然损失"""
            logging.debug(f"{time_}-选择的损失函数为:目标泊松分布的负对数似然损失")
            loss_ = self._poisson_error()
        elif idea == 'G':
            """高斯负对数似然损失"""
            logging.debug(f"{time_}-选择的损失函数为:高斯负对数似然损失")
            loss_ = self._gaussian_error()
        elif idea == 'B':
            """二元交叉熵"""
            logging.debug(f"{time_}-选择的损失函数为:二元交叉熵")
            loss_ = self._bce_error()
        else:
            logging.error(f"{time_}-没有该参数({idea})的损失函数")
            raise self.Error.LossError(f"{time_}-没有该参数({idea})的损失函数, 请更换")
        return loss_

    def Loss(self, output: Any, target: Any, loss: str = None):
        """
        损失函数的使用方法
        参数output 即 输入
        参数target 即 标签值
        loss 则表示选择的损失函数默认为均方差
        使用：
        loss = Loss(output, target, "m")
        ....
        loss.item()
        """
        if not self.LossFunc:
            self.LossFunc = self.loss(loss)
        self._loss = self.LossFunc(output, target)
        return self._loss

    def _mean_squared_error(self) -> Any:
        """均方差
        创建一个标准，用于测量输入中每个元素之间的均方误差（L2 范数）x和目标y.
        """
        return self.nn.MSELoss()

    def _mean_abs_error(self) -> Any:
        """平均绝对误差
        创建一个条件，用于测量输入中每个元素之间的平均绝对误差x和目标y
        """
        return self.nn.L1Loss()

    def _cross_entropy_error(self) -> Any:
        """交叉熵损失
        计算输入和目标之间交叉熵损失
        """
        return self.nn.CrossEntropyLoss()

    def _ctc_error(self) -> Any:
        """时间分类损失
        连接主义的时间分类损失
        """
        return self.nn.CTCLoss()

    def _nll_error(self) -> Any:
        """
        负对数似然损失
        """
        return self.nn.NLLLoss()

    def _poisson_error(self) -> Any:
        """
        目标泊松分布的负对数似然损失
        """
        return self.nn.PoissonNLLLoss()

    def _gaussian_error(self) -> Any:
        """
        高斯负对数似然损失
        """
        return self.nn.GaussianNLLLoss()

    def _bce_error(self) -> Any:
        """
        创建一个条件，用于测量目标和输入概率之间的二元交叉熵
        """
        return self.nn.BCELoss()

    def Optimizer(self, net: Any, lr: float = None, momentum: float = None, optimS: str = None) -> Any:
        """
        创建优化器 学习率默认0.01， 冲量默认为0.9
        返回该优化器， 也可使用模型.optimizer 获得该优化器， 前提是定义了优化器， 否则返回None

        """
        lr_set = self.setting["lr"]
        lr_ = lr_set.float if lr_set.value else self._lr
        momentum_set = self.setting["momentum"]
        momentum_ = momentum_set.float if momentum_set.value else self._momentum
        if lr:
            lr_ = lr
        if momentum:
            momentum_ = momentum
        optim_ = self.setting["optim"].value if self.setting["optim"].value else self._optim
        if optimS:
            optim_ = optimS
        """实现随机梯度下降（可选使用动量）"""
        _optimizer = self.optim.SGD(net.parameters(), lr=lr_, momentum=momentum_)
        if optim_:
            if optim_.title() == 'Rprop':
                """实现弹性反向传播算法"""
                _optimizer = self.optim.Rprop(net.parameters(), lr=lr)
            if optim_.title() == 'Adam':
                """随机梯度下降法"""
                _optimizer = self.optim.Adam(net.parameters(), lr=lr)
        self._optimizer = _optimizer
        logging.debug(f"{self.Time}选择学习率:{lr}, 冲量:{momentum_}, 优化算法:{optim_.title()}")
        return _optimizer

    @property
    def optimizer(self):
        return self._optimizer

    def module_save(self, net, optimizer, epoch, name: str = None, save: str = None) -> None:
        """
        模型保存方法
        需要提供网络原型，优化器原型，迭代次数
        可选参数
        name： 保存模型的主要名称可提供也可通过配置文件model_name设置
        save： 保存模型的路径，若不提供，将以当前路径 + model_path（配置文件中）保存 默认./cache/model
        当保存模型名已存在时将自动增加模型编号，此方法不允许自定义
        例：
        若 2022-4-10.pth已存在则会保存为2022-4-10(1).pth
        """
        self._ModuleDict = {
            "net": net.state_dict(),
            "optimizer": optimizer.state_dict(),
            "epoch": epoch,
        }
        self._save(name, save)

    def _save(self, name: str, save: str):
        """
        保存模型核心代码
        """
        from ..conf.os import join, BASE_PATH, isExists, mkdir
        from ..conf import recursion

        file = f'{name if name else self.setting["model_name"].value}-{self.Date}.pth'
        if not save:
            self.path_to = join(BASE_PATH,
                                self.setting["model_path"].value if self.setting["model_path"].value else "cache/model")
        else:
            self.path_to = save
        if not isExists(self.path_to):
            mkdir(self.path_to)
        self.path_to = join(self.path_to, file)
        self.torch.save(self._ModuleDict, recursion(self.path_to))
        logging.debug(f"保存模型，保存路径为({self.path_to})")

    def module_load(self, path: str, net: Any = None, optimizer: bool = False) -> tuple:
        """
        模型加载方法，
        path： 提供加载模型的完整路径
        net： 为网络的原型，
        optimizer： 为网络优化器，传入True 则选择为需要加载模型中保存的优化器，若模型中为保存优化器则会报错
        必填项path
        可选项net： 若不提供将只会加载迭代次数，若迭代次数未保存则返回为0
        最后都会返回一个元组，元组顺序已固定都为model， optimizer， epoch
        """
        model = net
        checkpoint = self.torch.load(path)
        if model:
            if "net" in checkpoint:
                model.load_state_dict(checkpoint["net"])
            else:
                model.load_state_dict(checkpoint)
        if optimizer:
            optimizer = self.Optimizer(model,
                                       float(self.setting["lr"].value) if float(self.setting["lr"].value) else self._lr,
                                       float(self.setting["momentum"].value)
                                       if float(self.setting["momentum"].value) else self._momentum
                                       )
            optimizer.load_state_dict(checkpoint["optimizer"])
        epoch = int(checkpoint.get('epoch', 0))
        logging.debug(f"加载模型，加载模型路径为({path})")
        return model, optimizer, epoch

    def __setitem__(self, key, value):
        """
        仅支持设置训练数据X的值
        设置方法self["X"] = data
        调用方法 self.X
        """
        if key == 'X':
            logging.debug(f"当前对训练变量进行赋值")
            self._X = value
        elif key == "optimizer":
            self._optimizer = value
        elif key == "T":
            self._T = value
        else:
            raise self.Error.SettingError(f"不支持增加该内容({key})")

    @property
    def X(self):
        """训练数据"""
        return self._X

    @property
    def T(self):
        """测试数据"""
        return self._T
