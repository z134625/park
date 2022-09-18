from . import database, index, table, user
from pymysql import Connection


__doc__ = """当前方法仅支持mysql 8.0以上使用，
目前支持功能：
1. 用户： 用户的创建，删除， 列出所有用户， 锁定与解锁用户， 用户改变密码， 用户授权， 与撤销权力， 显示用户权力
2. 数据库： 支持数据库创建， 数据库删除， 以及列出数据库
3. 索引： 支持 增加索引， 删除索引， 显示索引， 创建索引
4. 表： 支持表的创建，显示表， 表的结构， 修改表(添加列，改列名， 该列类型， 删除表)， 表重命名， 
清除表数据， 删除数据， 复制表， 修复表， 显示列， 锁表解锁表， 插入行，更新行， 替换行 删除行，查询操作（联结查找暂不支持）
"""


class ParkMysql:
    def __init__(self):
        self.connect = Connection()
