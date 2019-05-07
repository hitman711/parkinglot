from django.utils import timezone
from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _

from mptt.models import MPTTModel, TreeForeignKey
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.

class Company(models.Model):
    """ """
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
        help_text=_('User company relationship'),
        related_name='companies')
    name = models.CharField(
        _('name'),
        help_text=_('Name of the company'),
        max_length=100)

    def total_lot(self):
        """ """
        return self.venues.filter(category=Venue.LOT).count()
    
    def available_lot(self):
        """ """
        return self.venues.filter(
            category=Venue.LOT
        ).exclude(
            reservation__book_from__lte=timezone.now(),
            reservation__book_to__gte=timezone.now()
        ).count()

class LotPrice(models.Model):
    """ """
    HOUR = 'hour'
    DAY = 'day'
    DURATION_UNIT = (
        (HOUR, _('Hour')),
        (DAY, _('Day'))
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE,
        verbose_name=_('company'),
        help_text=_('Lot price list'),
        related_name='lot_prices'
    )
    name = models.CharField(
        max_length=100, verbose_name=_('name'),
        help_text=_('Lot price name'))
    duration = models.IntegerField(default=1)
    duration_unit = models.CharField(
        choices=DURATION_UNIT,
        max_length=10,
        verbose_name=_('duration_unit'),
        help_text=_('Lot reservation unit'))
    pre_paid_amount = models.DecimalField(
        default=0,
        max_digits=6, decimal_places=2,
        verbose_name=_('pre_paid'),
        help_text=_('Lot reservation pre paid amount'))
    amount = models.DecimalField(
        default=0,
        max_digits=6, decimal_places=2,
        verbose_name=_('amount'),
        help_text=_(
            'Amount to be paid for lot reservation based on duration'))
    overdue_amount = models.DecimalField(
        default=0,
        max_digits=6, decimal_places=2,
        verbose_name=_('overdue_amount'),
        help_text=_(
            'Amount to be added in total amount if reservation cross'
            'it\'s reservation time. Overcharge amount set based on duration')
    )

    def __str__(self):
        return '%s - %s' %(self.id, self.name)

class Venue(MPTTModel):
    """ """
    BUILDING = 'building'
    LOT = 'lot'
    FLOOR = 'floor'

    VENUE_CATEGORY = (
        (BUILDING, _('Building'),),
        (LOT, _('Lot'),),
        (FLOOR, _('Floor'))
    )

    name = models.CharField(_('name'),
        help_text=_('Venue name'),
        max_length=100)
    company = models.ForeignKey(Company,
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_('company'),
        help_text=_('Company relationship'),
        related_name='venues')
    category = models.CharField(_('category'),
        help_text=_('Venu Category'),
        choices=VENUE_CATEGORY,
        db_index=True,
        max_length=100)
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name=_('parent'),
        help_text=_('Child parent relationship'),
        related_name='children')
    venue_price = models.ForeignKey(
        LotPrice, on_delete=models.SET_NULL,
        null=True, verbose_name=_('venue_price'),
        help_text=_('Venue price relationship'),
        related_name='venue')

    def get_location(self):
        """ """
        location = ''
        if self.parent:
            if parent.category == self.FLOOR:
                location = '%s floor, ' % (self.parent.name)
        if self.company:
            location = location + '%s' % (self.company.name)
        return location

    def total_lot(self):
        """ """
        if self.category == self.LOT:
            return 0
        else:
            children = self.get_children()
            if not children:
                return 0
            return children.filter(category=Venue.LOT).count()
    
    def available_lot(self):
        """ """
        if self.category == self.LOT:
            return 0
        else:
            children = self.get_children()
            if not children:
                return 0
            return children.filter(
                category=Venue.LOT
            ).exclude(
                reservation__book_from__lte=timezone.now(),
                reservation__book_to__gte=timezone.now()
            ).count()

class Reservation(models.Model):
    """ """
    PENDING = 'pending'
    BOOKED = 'booked'
    ACTIVE = 'active'
    CLOSED = 'closed'
    CANCELED = 'canceled'

    RESERVATION_STATUS = (
        (PENDING, _('Pending')),
        (BOOKED, _('booked')),
        (ACTIVE, _('Active')),
        (CLOSED, _('Closed')),
        (CANCELED, ('Canceled')))
    
    PARTIAL_PAID = 'partial paid'
    FULL_PAID = 'full paid'
    
    PAYMENT_STATUS = (
        (PENDING, _('Payment pending')),
        (PARTIAL_PAID, _('Partial Paid')),
        (FULL_PAID, _('Full Paid'))
    )

    venue = models.ForeignKey(
        Venue, on_delete=models.CASCADE,
        verbose_name=_('venue'),
        help_text=_('Venue relationship'),
        related_name='reservation')
    book_from = models.DateTimeField(
        verbose_name=_('book_from'),
        help_text=_('Reservation start date time'))
    book_to = models.DateTimeField(
        verbose_name=_('book_to'),
        help_text=_('Reservation end date time'))
    license = models.CharField(
        max_length=20, verbose_name=_('license'),
        help_text=_('Vehicle license number'))
    phone_number = PhoneNumberField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, verbose_name=_('user'),
        help_text=_('User reservation relationship'))
    status = models.CharField(
        choices=RESERVATION_STATUS,
        default=PENDING,
        max_length=10,
        verbose_name=_('status'),
        help_text=_('Reservation status'))
    amount = models.DecimalField(
        verbose_name=_('amount'),
        help_text=_('Reservation amount to be paid'),
        default=0,
        max_digits=6, decimal_places=2)
    overdue_amount = models.DecimalField(
        default=0,
        verbose_name=_('overdue_amount'),
        help_text=_('Late fee charges to be paid'),
        max_digits=6, decimal_places=2
    )
    payment_status = models.CharField(
        choices=PAYMENT_STATUS, default=PENDING, 
        max_length=20,
        verbose_name=_('payment_status'),
        help_text=_('Reservation payment status'))
    total_amount = models.DecimalField(
        verbose_name=_('total_amount'),
        help_text=_('Final amount to be paid for reservation'),
        default=0,
        max_digits=6, decimal_places=2)
    total_amount_paid = models.DecimalField(
        verbose_name=_('total_amount'),
        help_text=_('Final amount to be paid for reservation'),
        default=0,
        max_digits=6, decimal_places=2)
    


class PaymentHistory(models.Model):
    """ """
    FREE = 'free'
    CASH = 'cash'
    CARD = 'card'

    PAYMENT_TYPE = (
        (FREE, _('Free')),
        (CASH, _('Cash')),
        (CARD, _('Card'))
    )

    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE,
        verbose_name=_('reservation'),
        help_text=_('Payment servation relationship'),
        related_name='payment_history')
    payment_type = models.CharField(
        choices=PAYMENT_TYPE,
        max_length=10, verbose_name=_('payment_type'),
        help_text=_('Payment method'))
    amount = models.DecimalField(
        default=0, max_digits=6, decimal_places=2,
        verbose_name=_('amount'),
        help_text=_('Amount paid for this payment method'))
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created'),
        help_text=_('Payment entry creation date'))