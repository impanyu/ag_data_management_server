from rest_framework import serializers
from .models import YouTubeChannel

class YouTubeChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeChannel
        fields = '__all__'
