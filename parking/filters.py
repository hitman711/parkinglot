import pytz
from datetime import datetime
import django_filters as filters
from django.conf import settings

from . import models

class NumberRangeFilter(filters.NumberFilter):

    def filter(self, qs, value):
        if value:
            time = datetime.fromtimestamp(
                    value).replace(tzinfo=pytz.utc)
            return qs.exclude(
                reservation__book_from__lte=time,
                reservation__book_to__gte=time
            )

class VenueFilter(filters.FilterSet):
    """ """
    category = filters.ChoiceFilter(
        choices=models.Venue.VENUE_CATEGORY)
    available = NumberRangeFilter()

    class Meta:
        model = models.Venue
        fields = ['available', 'company', 'parent']

class ReservationFilter(filters.FilterSet):
    """ """
    status = filters.ChoiceFilter(
        choices=models.Reservation.RESERVATION_STATUS)

    class Meta:
        model = models.Reservation
        fields = {
            
        }