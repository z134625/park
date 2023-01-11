from parkPro.tools import ParkLY, env, SettingParas, remove
import inherit


class New(ParkLY):
    _name = 'New'
    root_func = ['name']

    def name(self):
        # print(sys._getframe().f_code.co_filename)  # 当前文件名，可以通过__file__获得
        # print(sys._getframe(0).f_code.co_name)  # 当前函数名
        # print(sys._getframe(1).f_code.co_name)  # 调用该函数的函数名字，如果没有被调用，则返回<module>
        # print(sys._getframe(0).f_lineno)  # 当前函数的行号
        # print(sys._getframe(1).f_lineno)  # 调用该函数的行号
        print(
            ())

    def pas(self):
        print(3)
        self.name()


class New2(ParkLY):
    _inherit = 'New'
    root_func = ['name']

    def pas(self):
        # print(sys._getframe().f_code.co_filename)  # 当前文件名，可以通过__file__获得
        # print(sys._getframe(0).f_code.co_name)  # 当前函数名
        # print(sys._getframe(1).f_code.co_name)  # 调用该函数的函数名字，如果没有被调用，则返回<module>
        # print(sys._getframe(0).f_lineno)  # 当前函数的行号
        # print(sys._getframe(1).f_lineno)  # 调用该函数的行号
        print(2)
        super(New2, self).pas()


class New4(New):
    _inherit = 'New'
    root_func = ['name']
    parass = 123

    def pas(self):
        # print(sys._getframe().f_code.co_filename)  # 当前文件名，可以通过__file__获得
        # print(sys._getframe(0).f_code.co_name)  # 当前函数名
        # print(sys._getframe(1).f_code.co_name)  # 调用该函数的函数名字，如果没有被调用，则返回<module>
        # print(sys._getframe(0).f_lineno)  # 当前函数的行号
        # print(sys._getframe(1).f_lineno)  # 调用该函数的行号
        print(1)
        super(New4, self).pas()

class New3(ParkLY):
    _name = 'New3'
    _inherit = 'New'
    root_func = ['names']
    paras = SettingParas()
    monitor = ['names']

    def names(self):
        # print(sys._getframe().f_code.co_filename)  # 当前文件名，可以通过__file__获得
        # print(sys._getframe(0).f_code.co_name)  # 当前函数名
        # print(sys._getframe(1).f_code.co_name)  # 调用该函数的函数名字，如果没有被调用，则返回<module>
        # print(sys._getframe(0).f_lineno)  # 当前函数的行号
        # print(sys._getframe(1).f_lineno)  # 调用该函数的行号
        # print(dir(self.env['New']))
        # print(self.env['New'].__class__.__bases__[0])
        print(self.paras)
        self.env['New'].pas()
        a = self.env['setting']
        a.open(r'.\conf.txt')
        print(a.sudo()._a)
        a.give(self)
        a.give(self, content={'open': a.open})
        print(a)

        # self.env['New'].pas()


if __name__ == "__main__":
    env.load()
    # New3(_error=True, _warn=False, _cover=True)
    # New.pas = New4.pas
    # New()
    new = env['New']
    new.pas(park_time=True)
    print(new.speed_info)

    # @new(root=True)
    # def ps(self):
    #     s = self.env['inherit'].sudo()
    #     s.park()
    #
    #     self.root_func = []
    #     print(self.root_func)
    #     print(self.paras)
    #     print(self)
    #     self.names()
    #     self.open(r'.\conf.txt')
    #     print(self._a)
    #     print(self)
    #     # self.paras._set_list = ['1']
    #     print(self.paras._attrs)
    #     print(self.a)
    #     print(self.paras.update({
    #         '_attrs': {'a': 10}
    #     }))
    #     print(self.paras._attrs)
    #     print(self.a)
    #     print(self.paras._obj)
    #     print(self.a)
        # s = self.env['tools'].config(data='das阿斯顿', mode=2, timeout=None)
        # t = s.sudo()
        # print(t.result)
        # print(s.result)
    # print(new.with_paras(ds=True).paras.ds)
    # ps()
    # print(ne)
    # new.with_paras(gl=True, _warn=True, _cover=True)
    # new.paras.update({
    #     'root_func': [],
    #     '_attrs': {'a': 1}
    # })
    # new.paras.update({
    #     '_attrs': {'a': 2}
    # })
    # print(new.a)

    # obj = env['monitor']
    # print(obj)
    # obj.attr()

