import logging
import re
from typing import Any, Union


class ModuleCompile:
    def __init__(self,
                 module: Any,
                 net: Any = None,
                 epoch: int = 15,
                 ):
        """
        该类基于网络中pytorch模型基础，优化器，损失函数选取都，配置文件使用都基于模型中的配置方法
        在使用该类时，必须将导入数据在模型中
        """
        from ..torchs import TorchModule

        self._torch = __import__("torch")
        self.module = module
        if isinstance(self.module, TorchModule):
            self.device = self.module.device
        self.net = net
        self.epoch = epoch
        self.setting = self.module.setting
        if self.setting.epoch.value:
            self.epoch = self.setting.epoch.int

    def train(self, mode: Union[bool, str] = False,
              name: str = "Park",
              seek_optimal: bool = False,
              is_min: bool = True) -> None:
        """
        训练方法启动时将进行训练， 训练数据根据self.module.X 中的数据
        在初始化次类时会检测是否，存在数据。
        部分方法中使用的数据解释：
         min_loss 最小损失值
         min_loss_model 最小损失值的模型字典
         back_loss 上次迭代的平均损失值
         dif_num 达到优化平均损失次数
         传入参数解释：
         :param mode : 传入值格式 epoch-num num为数字 表示每迭代num次将保存一次模型
         :param name : 表示保存模型的标识名
         :param seek_optimal : 表示找出最优的迭代， 默认False， 当为True 时将检查每次迭代的平均loss值，到达一定程度时，将自动退出迭代
         :param is_min : 系统每次迭代都会查找整个迭代过程中最小损失值， 当开启时，最后会保存最小损失值的模型
        """
        from ...conf import Error
        from ...conf.setting import TrainProgressPark

        self.net.to(self.device)
        model_name = self.module.setting.model_name.value
        if name:
            model_name = name
        min_loss = None
        min_loss_model = None
        if not self.module.X:
            raise Error.DataError(f"没有设置模型的训练数据，请使用{self.module.__name__}['X'] = trainData设置")
        with TrainProgressPark(self.epoch) as park:
            back_loss = 0.0
            dif_num = 0
            for epoch in range(self.epoch):
                park.layer_epoch()
                total_loss = 0.0
                for data in self.module.X:
                    inputs, labels = self._data_optim(data)
                    outputs = self.net(inputs)
                    self.module.optimizer.zero_grad()
                    loss = self.module.Loss(outputs, labels)
                    loss.backward()
                    self.module.optimizer.step()
                    run_loss = loss.item()
                    total_loss += run_loss
                    park.layer_batch(len(self.module.X), run_loss=run_loss, total_loss=total_loss)

                    min_loss, min_loss_model = self._min_loss(min_loss=min_loss,
                                                              run_loss=run_loss,
                                                              epoch=epoch,
                                                              model_name=model_name,
                                                              min_loss_model=min_loss_model)

                if mode:
                    if not self._epoch_save(mode, epoch, run_loss, model_name):
                        mode = False

                seek_result = self._seek_optim(seek_optimal=seek_optimal,
                                               total_loss=total_loss,
                                               back_loss=back_loss,
                                               dif_num=dif_num
                                               )
                if seek_result is False:
                    break
                else:
                    if isinstance(seek_result, tuple):
                        back_loss, dif_num = seek_result
                    else:
                        logging.error("系统错误， 将不执行此操作(查找最优迭代，并推出),原因返回值应为元组数据但是实际为%s(%s)"
                                      % (type(seek_result), seek_result))

        self.module.module_save(self.net, optimizer=self.module.optimizer, epoch=self.epoch, name=model_name)
        if is_min:
            if min_loss_model is not None:
                self.module.module_save(**min_loss_model)

    def test(self, module_path: str = None) -> list:
        assert self.module.T, "请设置测试数据"
        input_list = []
        dif_list = []
        net, _, _ = self.module.module_load(self.module.path_to if not module_path else module_path, net=self.net)
        net.to(self.module.device)
        for data in self.module.T:
            inputs, labels = self._data_optim(data)
            inputs, labels = inputs.to(self.device), labels
            outputs = net(inputs)
            outputs = outputs.cpu().detach().numpy()
            labels = labels.cpu().numpy()
            dif = outputs - labels
            dif_list.append(dif)
            input_list.append(labels)
        data = [(i, j) for i, j in zip(input_list, dif_list)]
        return data

    def _epoch_save(self, mode: str, epoch: int, run_loss: float, model_name: str) -> bool:
        if isinstance(mode, str):
            pattern = re.compile(r"epoch-\d+")
            if re.search(pattern, mode):
                _, num = mode.split("-")
                if epoch % int(num) == 0 and epoch != 0:
                    self.module.module_save(self.net, optimizer=self.module.optimizer,
                                            epoch=epoch, name=f"epoch-%d-loss-%.6f-" % (epoch, run_loss)
                                                              + model_name)
                return True
        else:
            logging.error("传入数据格式错误，应得到epoch-num, 但是得到%s" % mode)
            print("\033[1,31,31m数据格式错误，将不执行次操作(迭代保存)\033[0m")
            return False

    def _data_optim(self, data: tuple) -> tuple:
        inputs, labels = data
        inputs, labels = inputs.to(self.device), labels.to(self.device)
        inputs, labels = self._torch.autograd.Variable(inputs), self._torch.autograd.Variable(labels)
        return inputs, labels

    def _min_loss(self, min_loss: Union[None, float],
                  run_loss: float,
                  epoch: int,
                  model_name: str,
                  min_loss_model: dict):
        if min_loss is None:
            min_loss = run_loss
        if run_loss < min_loss:
            min_loss = run_loss
            min_loss_model = {
                "net": self.net,
                "optimizer": self.module.optimizer,
                "epoch": epoch,
                "name": f"epoch-%d-min-loss-%.6f-" % (epoch, min_loss) + model_name
            }
        return min_loss, min_loss_model

    def _seek_optim(self, seek_optimal: bool, total_loss: float, back_loss: float, dif_num: int) -> Union[bool, tuple]:
        if seek_optimal:
            avg_loss = total_loss / len(self.module.X)
            dif_loss = abs(avg_loss - back_loss)
            back_loss = avg_loss
            if dif_loss / avg_loss <= self.setting.slow_loss.float if self.setting.slow_loss.value else 0.05:
                dif_num += 1
            else:
                dif_num = 0
            if dif_num >= self.setting.slow_loss_num.int if self.setting.slow_loss_num.value else 20:
                print("\n当前损失值下降较慢，预测接近最优，提前停止迭代")
                return False
        return back_loss, dif_num
