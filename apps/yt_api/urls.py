from django.urls import path,re_path
from .views import *

urlpatterns = [
    path('top-chinese-channels-subscribers/', YouTubeTopChineseChannelSubscribers.as_view(), name='top-chinese-channels-subscribers'),
    path('top-chinese-channels/', YouTubeTopChineseChannelList.as_view(), name='top-chinese-channels'),
    path('get-hello/', GetHello.as_view(), name='get-hello'),
    # Matches any html file
    re_path(r'^.*\.*', pages, name='pages'),
]