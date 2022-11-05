from torch import optim, nn
from park.ai.program.program import ProgramModule
from park.utils.data import Normalization
from park.utils.numpys.tools import add_row, add_column
from test_temp import Data
from park.utils.media.tools import code


class LDA(ProgramModule):

    def optimizer(self):
        return optim.Adam(params=self.net().parameters(), lr=1e-4)

    def net(self):
        class BPNet(nn.Module):
            def __init__(self):
                super(BPNet, self).__init__()
                self.bp = nn.Sequential(
                    nn.Linear(2, 3),
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

        return BPNet()


if __name__ == '__main__':
    da = Data()
    lda = LDA(module_path="test/cache/model/P380CL-2022-5-5(2).pth",
              mode="quick", setting_path="./config.ini")
    for data, file in da.make_dataset():
        # image, result = code()
        # image.show()
        # input_ = input("请输入验证码")
        # if input_ != result:
        #     break
        scaler = Normalization(range_max_min=(-1, 1))
        scaler1 = Normalization(range_max_min=(0, 1))
        input_data = add_row(data[:-1], [[600]], after=False)
        input_data = scaler1.fit_data(input_data.reshape(-1, 1))
        # input_data1 = add_row(data[:-2], [[600], [600]], after=False)
        # input_data1 = scaler1.fit_data(input_data1.reshape(-1, 1))
        data = scaler1.fit_data(data.reshape(-1, 1))
        inputs = scaler.fit_data(da.inputs.reshape(-1, 1))
        inputs = add_column(inputs, input_data)
        lda.test_data = inputs
        lda.test_labels = data
        x = lda.start(command="test")
        for i in x:
            for j in i:
                print(scaler1.reduction_data(j)[0])
            break
        break
