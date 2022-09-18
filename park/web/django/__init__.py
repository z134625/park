__doc__ = """
django 
1. 创建工程 工程名为projectname
django-admin startproject projectname 
2. 创建app应用 应用名为user
django-admin startapp user /
cd projectname;
python manage.py startapp user
3. 路由设置
from django.urls import path, re_path, include, url
path 为配置统一路由，即路由地址固定的：
path('user/', view)
path('/<int: user>/', view) 此时匹配的路由为/123/
其中默认支持的转化器有： str(字符串) int(整数) slug(字母、数字、下划线) uuid(格式化的uuid) path(匹配任何非空字符)

re_path 为配置不定路由， 且有一定规律，可用正则代替的：
re_path(r'^user/(?P<name>正则)/park$', view)
若正则为[0-9]{1, 3}
则能匹配 user/0/park or user/12/park

include 为设置主路由下的分支路由路径：
path('user/', include('user.urls')
若app user下的urls为：
path('login/', view)
则访问： 
user/login/
url 为path与re_path集合都可用， 但后续版本的django不建议使用

4. 配置文件setting 
在setting.py 中的变量信息可通过
from django.conf import settings
settings.BASE_DIR 调用
BASE_DIR 表示工作路径
在调试过程中DEBUG需要开启，即若视图函数有错误会显示错误原因
ALLOWED_HOST 表示允许的主机
INSTALLED_APPS 表示该工程的app应用，若自行添加后需要在该处增加自己创建的app名
MIDDLEWARE 表示工程的中间件，可在此处添加设置访问限制
"""
import re


pattern = re.compile(r'(?)')
