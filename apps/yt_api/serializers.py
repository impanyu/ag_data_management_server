from rest_framework import serializers
from .models import YouTubeChannel

class YouTubeChannelSerializer(serializers.ModelSerializer):
    subscribers = serializers.IntegerField()
    class Meta:
        model = YouTubeChannel
        fields = ['channel_id', 'title', 'description', 'subscribers']
