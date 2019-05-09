import pytz
from datetime import datetime
import django_filters as filters
from django.conf import settings
from django.utils.translation import gettext as _

from . import models


class NumberRangeFilter(filters.NumberFilter):
    """ Custom number range filter to find out available
    venue for reservation
    """

    def filter(self, qs, value):
        if value is not None:
            if value:
                time = datetime.fromtimestamp(
                    value).replace(tzinfo=pytz.utc)
                return qs.exclude(
                    reservation__book_from__lte=time,
                    reservation__book_to__gte=time
                )
        return super().filter(qs, value)


class VenueFilter(filters.FilterSet):
    """ Venue filters
    """
    category = filters.ChoiceFilter(
        choices=models.Venue.VENUE_CATEGORY)
    available = NumberRangeFilter(
        help_text=_('Check venue availability filter')
    )

    class Meta:
        model = models.Venue
        fields = ['available', 'company', 'parent']


class ReservationFilter(filters.FilterSet):
    """ """
    status = filters.ChoiceFilter(
        choices=models.Reservation.RESERVATION_STATUS,
        help_text=_(
            'resevation status list %s' % (
                str(
                    list(
                        dict(
                            models.Reservation.RESERVATION_STATUS
                        ).keys()
                    )
                )
            )
        ))

    class Meta:
        model = models.Reservation
        fields = {

        }
