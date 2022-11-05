import sys
# import park
from park.utils.xlrds import ExcelOpen

if __name__ == '__main__':
    # SelfStart(hide_terminal=True).close()
    _names = sys.builtin_module_names
    # print(sys.modules.__len__())
    # print(sys.version)
    # print(sys.hash_info)
    import re

    f = open("C:\\Users\\PC\\Desktop\\02_数据整理_素材.txt", "r", encoding="utf-8")
    ex = ExcelOpen("C:\\Users\\PC\\Desktop\\02_数据整理_素材.xlsx", mode="w")

    files = f.readlines()
    write_f = {}
    pattern = re.compile(r"\t+")
    for file in files:
        file = file.strip('"\ufeff')
        file = file.strip('"\n')
        s = re.split(pattern=pattern, string=file)
        ex.write_rows(s, sheet="sheet1", is_row=True)
    ex.save()
