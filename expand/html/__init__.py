from . import web, flask_base
from . import api

from parkPro.utils.api import api_register

api_register(api_func=api)
