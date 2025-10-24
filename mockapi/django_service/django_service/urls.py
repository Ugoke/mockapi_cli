from .dynamic_view import dynamic_view
from django.urls import re_path


urlpatterns = [
    re_path(r'^(?P<path>.*)$', dynamic_view),
]