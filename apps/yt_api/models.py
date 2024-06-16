from django.db import models

class YouTubeChannel(models.Model):
    channel_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    icon_url = models.URLField(max_length=200, blank=True, null=True)  # Add this field
   
    def __str__(self):
        return self.title


class YouTubeChannelSubscribers(models.Model):
    channel_id = models.CharField(max_length=255, unique=True)   
    subscribers = models.BigIntegerField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.channel_id