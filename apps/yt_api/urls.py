from django.urls import path
from .views import YouTubeChannelList

urlpatterns = [
    path('top-channels/', YouTubeChannelList.as_view(), name='top-channels'),
]