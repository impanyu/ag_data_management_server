from django.urls import path,re_path
from .views import *

urlpatterns = [
    path('top-chinese-channels-historic/', YouTubeTopChineseChannelListHistoric.as_view(), name='top-chinese-channels-historic'),
    path('top-chinese-channels-realtime/', YouTubeTopChineseChannelListRealTime.as_view(), name='top-chinese-channels-realtime'),
    path('get-hello/', GetHello.as_view(), name='get-hello'),
    # Matches any html file
    re_path(r'^.*\.*', pages, name='pages'),
]