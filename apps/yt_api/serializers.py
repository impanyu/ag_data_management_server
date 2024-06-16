from rest_framework import serializers
from .models import *
class YouTubeChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeChannel
        fields = '__all__'


class YouTubeChannelSubscribersSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeChannelSubscribers
        fields =  ['channel_id', 'subscribers']