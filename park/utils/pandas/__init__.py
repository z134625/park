from ...conf.setting import install_module

if __name__ == "park.utils.pandas":
    if install_module("pandas", "pandas~=1.3.0") != 0:
        raise SystemError("模块xlwt下载失败")