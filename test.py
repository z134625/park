from parkPro.tools import Paras, SettingParas



if __name__ == '__main__':
    p = Paras()
    p1 = SettingParas()

    print(p._suffix_ini)
    print(p._allow_set)
    print(p1._suffix_ini)
    print(p1._allow_set)
    p1.update({'_suffix_ini': 's'})
    print(p1._suffix_ini)