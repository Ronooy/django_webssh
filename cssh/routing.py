#!/usr/bin/env python
from django.conf.urls import url
from .consumers import EchoConsumer


websocket_urlpatterns=[
    url(r'^ssh/$',EchoConsumer)
]