import functools
import re
import sys
import warnings

from typing import Any, Union
from collections.abc import Iterable, Generator
from abc import ABCMeta, abstractmethod

from matplotlib import pyplot as plt

from park.conf.os import base, join, mkdir, listPath, isType
from park.conf.setting import CurrencySetting
from park.utils.numpys.tools import Ndarray


class ProgramModule(metaclass=ABCMeta):
    setting = None
    compile_module = None

    def __init__(self,
                 data: Union[Ndarray] = None,
                 labels: Union[Ndarray] = None,
                 test_data: Union[Ndarray] = None,
                 test_labels: Union[Ndarray] = None,
                 mode: str = "default",
                 setting_path: Union[list, tuple, str, Generator] = None,
                 frame: str = "torch",
                 batch_size: int = 16,
                 module_path: str = None,
                 ):
        self.data = data
        self.labels = labels
        self.test_data = test_data
        self.test_labels = test_labels
        self.mode = mode
        self.setting_path = setting_path
        self.frame = frame.lower()
        self.batch_size = batch_size
        self.module_path = module_path
        assert isinstance(self.batch_size, int) and self.batch_size % 2 == 0, \
            "batch_size错误，请传入整数，并且是2的倍数的数字"
        self._read_setting()

    def _read_setting(self) -> None:
        from ..torchs import TorchModule
        self.setting = CurrencySetting()
        if isinstance(self.setting_path, str):
            self.setting.load(self.setting_path)
        elif isinstance(self.setting_path, Iterable):
            for item in self.setting_path:
                self.setting.load(item)
        self.module = TorchModule(version=True, conf=True)
        from .torchs import ModuleCompile
        net = self.net()
        net.to(self.module.device)
        assert net, "未设置模型方法， 或者未返回模型"
        self.compile_module = ModuleCompile(self.module, net=net)

    def _resolving(self) -> dict:
        assert self.mode, "模式不允许为空"
        if self.mode == "slow":
            dict_ = {
                "mode": f"epoch-{self.batch_size // 20}",
                "seek_optimal": False,
                "is_min": True,
            }
        elif self.mode == "quick":
            dict_ = {
                "mode": False,
                "seek_optimal": True,
                "is_min": True,
            }
        else:
            dict_ = {
                "mode": f"epoch-{self.batch_size // 10}",
                "seek_optimal": False,
                "is_min": True,
            }
        return dict_

    def _datasets(self) -> tuple:
        test_dataset = None
        dataset = None
        if self.setting.batch_size.value:
            self.batch_size = self.setting.batch_size.int
        if self.frame == "torch":
            from torch.utils.data import DataLoader, TensorDataset
            from torch import from_numpy
            if self.data is not None and self.labels is not None:
                dataset = TensorDataset(from_numpy(self.data).float(), from_numpy(self.labels).float())
                dataset = DataLoader(dataset, shuffle=True, batch_size=self.batch_size)
            if self.test_data is not None and self.test_labels is not None:
                test_dataset = TensorDataset(from_numpy(self.test_data).float(), from_numpy(self.test_labels).float())
                test_dataset = DataLoader(test_dataset, shuffle=True, batch_size=self.batch_size)
            return dataset, test_dataset

    @abstractmethod
    def net(self):
        """
        创建模型
        最后返回应为网络模型
        """
        pass

    @abstractmethod
    def optimizer(self):
        """
        创建优化器
        """
        pass

    def start(self, command: str = "train"):
        self.module["optimizer"] = self.optimizer()
        if self.setting is None or self.setting.set_dict is {}:
            warnings.warn("未设置配置文件， 程序将选择默认配置进行", RuntimeWarning)
        dataset, test_data = self._datasets()
        if dataset:
            self.module["X"] = dataset
        if test_data:
            self.module["T"] = test_data
        if command == "train":
            return self.compile_module.train(**self._resolving())
        elif command == "test":
            return self._test()

    def _test(self):
        return self.compile_module.test(self.module_path)


def model_test_number(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> dict:
        from torch.autograd import Variable
        from ...utils.data import Normalization
        analysis = {}
        model_path: Union[list, tuple, str] = kwargs.get("model_path", None)
        model: Any = kwargs.get("model", None)
        net: Any = kwargs.get("net", None)
        is_show: bool = kwargs.get("is_show", False)
        is_save: bool = kwargs.get("is_save", False)
        save_path: str = kwargs.get("save_path", './cache/plt')
        plt_title: str = kwargs.get("plt_title", "")
        xlabel: str = kwargs.get("xlabel", "X")
        ylabel: str = kwargs.get("ylabel", "Y")
        show_excel: bool = kwargs.get("show_excel", False)
        normal: bool = kwargs.get("normal", True)
        scaler_input = Normalization(range_max_min=None)
        scaler_output = Normalization(range_max_min=None)
        if normal:
            scaler_input = Normalization(range_max_min=(0, 1))
            scaler_output = Normalization(range_max_min=(0, 1))
            pattern1 = re.compile(r'normal_(_?\d+)_(_?\d+)')
            pattern2 = re.compile(r'normal_none')
            range_max_min = filter(lambda x: re.match(pattern1, x) or re.match(pattern2, x), kwargs.keys())
            for item in range_max_min:
                max_min = re.match(pattern1, item)
                if max_min:
                    max_ = max_min.group(1)
                    max_ = int(max_.replace('_', '-'))
                    min_ = max_min.group(2)
                    min_ = int(min_.replace('_', '-'))
                    if kwargs.get(item) == 'input':
                        scaler_input = Normalization(range_max_min=(max_, min_))
                    if kwargs.get(item) == 'output':
                        scaler_output = Normalization(range_max_min=(max_, min_))
                else:
                    if kwargs.get(item) == 'input':
                        scaler_input = Normalization(range_max_min=None)
                    if kwargs.get(item) == 'output':
                        scaler_output = Normalization(range_max_min=None)
        if plt_title:
            plt_title += '-'
        assert model_path and isinstance(model_path, Iterable), "请提供模型方法，并且是可迭代形式"
        assert model, "请提供模型地址可以是单独一个模型也可为一组模型"
        # datas: Any = func(*args, **kwargs)
        # assert isinstance(datas, Iterable), "返回的数据必须是可迭代的"
        if isinstance(model_path, str) and isType(model_path, form="dir"):
            files = listPath(model_path, doc=True, splicing=True, like=kwargs.get("like", None))
        else:
            files = model_path
            if isinstance(model_path, str):
                files = [model_path]
        for i, path in enumerate(files):
            print(f"\033[1;31;31m\r测试第{i + 1}个模型中...\033[0m")
            for j, item_tuple in enumerate(func(*args, **kwargs)):
                print(f"\033[1;31;31m\r---测试第{j + 1}个数据中..\033[0m", end="")
                if item_tuple.__len__() == 3:
                    data, inputs, file = item_tuple
                elif item_tuple.__len__() == 2:
                    file = None
                    data, inputs = item_tuple
                else:
                    raise ValueError("生成器生成的数据长度不对应为3，或2， 顺序应为(data, inputs, file)")
                scaler_output.fit_data(data)
                net_load, _, _ = model.module_load(path,
                                                   net=net)
                net_load.cpu()
                inputs = scaler_input.fit_data(inputs)
                inputs = model.np_tensor(inputs)
                inputs = Variable(inputs)
                pred = net(inputs.float())
                pred_test = pred.view(-1).cpu().data.numpy()
                pred_test = scaler_output.reduction_data(pred_test)
                _plt_draw(data, pred_test, scaler_input.reduction_data(inputs), name=f"{plt_title}{i+1}-{j+1}-",
                          is_show=is_show, is_save=is_save, save_path=save_path, xlabel=xlabel, ylabel=ylabel)
                dict1 = analysis.get(base(path), {})
                dict2 = {f"{file if file else 'data'}": _error_temp(data, pred_test, file, **kwargs)}
                analysis[base(path)] = {**dict1, **dict2}

                sys.stdout.flush()
                print(f"\033[1;32;32m\r---测试第{j + 1}个数据完成\033[0m")

            sys.stdout.flush()
            print(f"\033[1;32;32m\r测试第{i + 1}个模型完成\033[0m")
        if show_excel:
            _dict_analysis(analysis=analysis)
        return analysis
    return wrapper


def _error_temp(data: Ndarray, test: Ndarray, file: str, **kwargs) -> dict:
    total = len(data)
    error_5 = []
    error_10 = []
    error_15 = []
    error_100 = []
    print_ = []
    error_ = {}
    for i in kwargs:
        if kwargs[i]:
            print_x = str(i)
            pattern = re.compile(r'print_(\d+)')
            result = re.search(pattern, print_x)
            if result:
                print_.append(int(result.group(1)))
    for i, (x1, x2) in enumerate(zip(data, test)):
        dif_ = abs(x1 - x2)
        if dif_ > 5:
            error_5.append(i)
        if dif_ > 10:
            error_10.append(i)
        if dif_ > 15:
            error_15.append(i)
        if dif_ > 100:
            error_100.append(i)
        for j in print_:
            if dif_ > j:
                s = error_.get(str(j), [])
                s.append(i)
                error_[str(j)] = s
    if error_:
        if file:
            print("文件路径：" + file)
        for item in error_.items():
            print('\n')
            print(item)
        print("*" * 50)
    return {
        "误差-5": [error_5.__len__(), "%.3f" % (error_5.__len__() / total)],
        "误差-10": [error_10.__len__(), "%.3f" % (error_10.__len__() / total)],
        "误差-15": [error_15.__len__(), "%.3f" % (error_15.__len__() / total)],
        "误差-100": [error_100.__len__(), "%.3f" % (error_100.__len__() / total)],
    }


def _plt_draw(data: Ndarray, pred_test: Ndarray, inputs: Ndarray, name: str,
              is_show: bool = False, is_save: bool = False, save_path: str = './cache/plt',
              xlabel: str = "X", ylabel: str = "Y") -> None:
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    path = save_path
    mkdir(path)
    plt.figure()
    plt.plot(data, 'r', label='真实数据')
    plt.plot(pred_test, 'b', label='拟合数据')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f"{name}数据分析")
    plt.legend()
    if is_show:
        plt.show()
    if is_save:
        plt.savefig(join(path, f"{name}数据.png"))
    plt.figure()
    inputs = inputs[:, 0]
    size = inputs.size(0)
    x = inputs.reshape(size)
    y = pred_test.reshape(size)
    plt.errorbar(x, y, yerr=(y - data.reshape(size)))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f"{name}误差线")
    if is_show:
        plt.show()
    if is_save:
        plt.savefig(join(path, f"{name}误差线.png"))


def _dict_analysis(analysis: dict) -> None:
    for item in analysis:
        print("模型：" + item)
        print("*" * 50)
        for d in analysis[item]:
            print("数据：" + d)
            print("-" * 50)
            for i in analysis[item][d]:
                val = analysis[item][d][i]
                print(i + "\t%d\t误差率:%s" % (val[0], val[1]))
            print("+" * 50)
