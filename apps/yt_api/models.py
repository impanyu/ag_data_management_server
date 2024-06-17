from django.db import models


class YouTubeChannel(models.Model):
    channel_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    icon_url = models.URLField(max_length=255, blank=True, null=True)
    join_date = models.DateTimeField(blank=True, null=True)  # Add join_date field
    location = models.CharField(max_length=255, blank=True, null=True)  # Add location field

    def __str__(self):
        return self.title



class YouTubeChannelSubscribers(models.Model):
    channel_id = models.CharField(max_length=255)   
    subscribers = models.BigIntegerField()
    last_updated = models.DateTimeField()

    def __str__(self):
        return self.channel_id