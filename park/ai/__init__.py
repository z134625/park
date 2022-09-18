
__doc__ = """
当配置文件选择frame 选择pytorch 是将有
  Loss，  ：Loss(output, target, loss) 配置文件提供loss 输入loss 默认从配置读取也可设置
  Weight， ：Weight (net, lr, momentum, optimS) net必选为输入网络 lr 默认0.01 ，momentum 默认0.9也可从配置文件读取，
                                                optimS默认从配置文件读取也可指定
  program、 ：program()将保存模型 program.load()将加载已有模型
"""


