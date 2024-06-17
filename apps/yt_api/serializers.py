from rest_framework import serializers
from .models import *
class YouTubeChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = '__all__'


class YouTubeChannelSubscribersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelSubscribers
        fields =  ['channel_id', 'subscribers']