import pandas as pd
from collections.abc import Generator

from torch.utils.data import TensorDataset, DataLoader
from torch import nn

from park.decorator.timer import timer
from park.ai.program.program import model_test_number
from park.utils.data import Normalization
from park.conf.setting import setting, Command
from park.conf.os import (
    listPath,
    join,
    absPath,
    base,
)
from park.ai.torchs import TorchModule
from park.ai.program.torchs import ModuleCompile
from park.utils.numpys.tools import asarray_data, add_row, add_column
from park.utils.xlrds import ExcelOpen
# from threading import Thread

import warnings


warnings.filterwarnings("ignore", category=UserWarning)

setting.load("./config.ini", log=True)
torch_module = TorchModule()


class Data:
    def __init__(self, path):
        self.path = path
        self.pd_data = {}
        self.inputs = None

    def read_data(self) -> Generator:
        path = absPath(setting.data_path.value)
        files = listPath(path, doc=True, splicing=True)
        for file in files:
            file_path = join(path, file)
            data = pd.read_csv(file_path)
            self.inputs = asarray_data([list(map(lambda x: 0.012 * int(x), data.index))])
            yield data.values, file

    def make_dataset(self) -> Generator:
        for item, file in self.read_data():
            yield asarray_data(item), file


class BPNet(nn.Module):
    def __init__(self):
        super(BPNet, self).__init__()
        self.bp = nn.Sequential(
            nn.Linear(1, 3),
            nn.Mish(),
            nn.Linear(3, 6),
            nn.Mish(),
            nn.Linear(6, 3),
            nn.Mish(),
            nn.Linear(3, 1),
            nn.Mish(),
        )

    def forward(self, x):
        x = self.bp(x)
        return x


class MainFunc:
    net = BPNet()
    net.to(torch_module.device)
    com = ModuleCompile(module=torch_module, net=net, epoch=setting.epoch.int)

    def train(self):
        da = Data(setting.train_data.value)
        datas = da.make_dataset()
        for data, _ in datas:
            scaler = Normalization(range_max_min=(-1, 1))
            scaler1 = Normalization(range_max_min=(0, 1))
            # input_data = add_row(data[:-1], [data[0]], after=False)
            # input_data = scaler1.fit_data(input_data.reshape(-1, 1))

            # input_data1 = add_row(data[:-2], [[600], [600]], after=False)
            # input_data1 = scaler1.fit_data(input_data1.reshape(-1, 1))

            data = scaler1.fit_data(data.reshape(-1, 1))
            inputs = scaler.fit_data(da.inputs.reshape(-1, 1))
            # inputs = add_column(inputs, input_data)
            # inputs = add_column(inputs, input_data1)
            torch_module.Optimizer(net=self.net, lr=setting.lr.float)
            inputs = torch_module.np_tensor(inputs)
            labels = torch_module.np_tensor(data)

            data_set = TensorDataset(inputs.float(), labels.float())
            torch_module["X"] = DataLoader(data_set, shuffle=True, batch_size=setting.batch_size.int)
            self.com.train(mode=False,
                           seek_optimal=True,
                           is_min=False,
                           name=base(setting.model_name.value))

    @model_test_number
    def test(self, **kwargs):
        da = Data(setting.test_data.value)
        datas = da.make_dataset()
        for data, file in datas:
            scaler = Normalization(range_max_min=(0, 1))
            scaler2 = Normalization(range_max_min=(-1, 1))
            # input_data = add_row(data[:-1], [data[0]], after=False)
            # input_data = scaler.fit_data(input_data.reshape(-1, 1))
            # input_data1 = np.row_stack((array_data([[600], [600]]), data[:-2]))
            # input_data1 = scaler.fit_data(input_data1.reshape(-1, 1))
            inputs = scaler2.fit_data(da.inputs.reshape(-1, 1))
            # inputs = add_column(inputs, input_data)
            # inputs = np.column_stack((inputs, input_data1))
            yield data, inputs

    @timer(msg="热轧板温度核验系统")
    def main(self):
        if "train" in Command:
            self.train()
        elif "test" in Command:
            s = self.test(model_path=setting.model_path.value, like=setting.model_like.value,
                          model=torch_module, net=self.net, is_show=True, print_100=False,
                          is_save=False, show_excel=False, save_path=setting.save_path.value, xlabel="时间", ylabel="温度",
                          normal=True, normal_0_1="output", normal_none="input")
        elif "export" in Command:
            s = self.test(model_path=setting.model_path.value, like=setting.model_like.value,
                          model=torch_module, net=self.net, is_show=True,
                          is_save=False, show_excel=False,
                          normal=True, normal_0_1="output", normal_none="input")
            with ExcelOpen(setting.excel.value, mode="w") as f:
                f.write_dicts(s, heard=["数据源或错误分类", "数据量", "错误率"])
            f = ExcelOpen("./模型评估统计.xls", mode="w")
            f.write_dicts(s, heard=["数据源或错误分类", "数据量", "错误率"])
            f.save()


if __name__ == '__main__':
    # Cache(class_=["model"], all_=True)
    MainFunc().main()


