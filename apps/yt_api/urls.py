from django.urls import path
from .views import *

urlpatterns = [
    path('top-chinese-channels-historic/', YouTubeTopChineseChannelListHistoric.as_view(), name='top-chinese-channels-historic'),
    path('top-chinese-channels-realtime/', YouTubeTopChineseChannelListRealTime.as_view(), name='top-chinese-channels-realtime'),
]