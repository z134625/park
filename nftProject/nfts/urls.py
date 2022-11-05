from django.urls import path, re_path
from . import views as view


urlpatterns = [
    path('nft/', view, name='nfts'),
    re_path(r'^nft/(?P<type>[a-zA-Z0-9]{11})/?$', view, name='nft'),
]
