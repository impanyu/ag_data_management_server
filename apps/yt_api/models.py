from django.db import models

class YouTubeChannel(models.Model):
    channel_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    


    def __str__(self):
        return self.title


class YouTubeChannelSubcribers(models.Model):
    #channel_id = models.CharField(max_length=255, unique=True)
    channel = models.ForeignKey(YouTubeChannel, on_delete=models.CASCADE)

    subscribers = models.BigIntegerField() 
    last_updated = models.DateTimeField(auto_now_add=True,db_index=True)


    def __str__(self):
        return self.channel.title