import time
import easygui
from easygui.boxes.choice_box import ChoiceBox

login_info = ["账号", "密码"]
login_state = False


def login_gui(msg: str = "登录"):
    easygui.multpasswordbox(msg, "", login_info, callback=verification_password)


def verification_password(main_box):
    global login_state

    class Choice(ChoiceBox):
        def callback_ui(self, ui, command, choices):
            global login_state
            if command == 'update':  # OK was pressed
                self.choices = choices
                if self.callback:
                    # If a callback was set, call main process
                    self.callback(self)
                else:
                    self.stop()
            elif command == 'x':
                self.stop()
                self.choices = None
                main_box.msg = "登录"
                login_state = False
            elif command == 'cancel':
                self.stop()
                self.choices = None
                main_box.msg = "登录"
                login_state = False

    def show():
        global login_state
        login_state = True
        while True:
            choice = ["总传感器的读数", "分传感器的读数", "标定图"]
            mb = Choice("请选择查看的内容", "数据信息", choice, preselect=0,
                        multiple_select=False,
                        callback=None)
            reply = mb.run()
            if reply is None:
                # login_state = False
                break
            else:
                if reply == "总传感器的读数":
                    msg_show(title=reply)
                elif reply == "分传感器的读数":
                    msg_show(title=reply)
                elif reply == "标定图":
                    pic_show(title=reply)

    def msg_show(title):
        easygui.msgbox("123", title, "关闭")

    def pic_show(title):
        easygui.buttonbox("", title, choices=["关闭"], image=r"D:\Desktop\c4onetwo.png")

    user, password = main_box.values
    if user == password and user and password:
        if not login_state:
            main_box.msg = "登录成功"
            show()

    else:
        main_box.msg = "密码错误或账号不存在"
        return main_box


def main():
    login_gui()


if __name__ == '__main__':
    main()
