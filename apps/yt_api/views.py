from rest_framework import generics
from .models import *
from .serializers import YouTubeChannelSerializer
from django.utils.timezone import now, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import OuterRef, Subquery, F

class YouTubeChannelList(generics.ListAPIView):
    serializer_class = YouTubeChannelSerializer

    def get_queryset(self):
        try:
            # Get the latest timestamp from the YouTubeChannel table
            latest_timestamp = YouTubeChannelSubscribers.objects.latest('last_updated').last_updated
            # Filter the channels updated at the latest timestamp and order them by subscribers
            #return YouTubeChannelSubscribers.objects.filter(last_updated=latest_timestamp)#.order_by('-subscribers')[:100]
        
             # Subquery to get the subscribers count from YouTubeChannelSubscribers
            latest_subscribers = YouTubeChannelSubscribers.objects.filter(
                channel=OuterRef('pk'),
                last_updated=latest_timestamp
            ).values('subscribers')[:1]

            # Annotate the YouTubeChannel queryset with the subscribers count
            queryset = YouTubeChannel.objects.annotate(
                subscribers=Subquery(latest_subscribers)
            ).order_by('-subscribers')

            return queryset
        except ObjectDoesNotExist:
            # Return an empty queryset if no data is found
            return YouTubeChannel.objects.none()

