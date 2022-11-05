from park.sql.mysql.database import create_database, show_databases, drop_database
from park.sql.mysql.user import create_user
from park.sql import mysql
# from park.conf.setting import setting

# setting.load("./config.ini")

if __name__ == '__main__':
    print(mysql.index.create_index(table="user", column="username", index="user1", db="hf_line"))
    print(drop_database(db="niu"))
    print(show_databases())
    print(create_user(username="park", password="123"))
