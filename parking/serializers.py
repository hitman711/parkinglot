""" """
import math

from parkinglot.fields import TimestampField
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext as _

from rest_framework import serializers, exceptions
from rest_framework.authtoken.models import Token

from . import models


class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'username')

    def validate_email(self, value):
        value = value.lower()
        return value

    def create(self, validated_data):
        try:
            instance = super(
                RegistrationSerializer, self).create(validated_data)
            instance.set_password(validated_data['password'])
            instance.save()
            return instance
        except Exception as e:
            raise exceptions.APIException(
                _('Service temporarily unavailable, try again later.')
            )

    def to_representation(self, instance):
        return {
            'message': _('User generated successfully')
        }


class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=100,
        help_text=_('User unique validation key')
    )

    class Meta:
        model = User
        fields = ('username', 'password')

    def validate(self, validated_data):
        """ """
        user = authenticate(
            request=self.context.get('request'),
            username=validated_data['username'],
            password=validated_data['password'])
        if user is None:
            raise serializers.ValidationError(
                _('Invalid username and password')
            )
        token, new = Token.objects.get_or_create(user=user)
        self.instance = user
        return validated_data

    def to_representation(self, instance):
        """ """
        return UserDetailSerializer(instance).data


class UserDetailSerializer(serializers.ModelSerializer):
    """ """
    authentication_code = serializers.CharField(
        max_length=40, source='auth_token.key')
    company_id = serializers.IntegerField(
        default=0)
    reservation_count = serializers.IntegerField(
        default=0, help_text=_(
            'Total no. of reservation user had till now'
        )
    )

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name',
            'email', 'company_id', 'authentication_code',
            'username', 'reservation_count')
        read_only_fields = (
            'id', 'company_id', 'authentication_code',
            'reservation_count')

    def to_representation(self, instance):
        representation = super(
            UserDetailSerializer, self).to_representation(instance)
        company = instance.companies.last()
        if company:
            representation['company_id'] = company.id
        representation['reservation_count'] = instance.user_reservation.count()
        return representation


class CompanySerializer(serializers.ModelSerializer):
    """ """
    total_lot = serializers.IntegerField(default=0, read_only=True)
    available_lot = serializers.IntegerField(default=0, read_only=True)

    class Meta:
        model = models.Company
        fields = ('id', 'name', 'total_lot', 'available_lot')
        read_only_fields = ('total_lot', 'available_lot')


class VenueTreeSerializer(serializers.ModelSerializer):
    """ """
    total_lot = serializers.IntegerField(default=0, read_only=True)
    available_lot = serializers.IntegerField(default=0, read_only=True)

    class Meta:
        model = models.Venue
        fields = ('id', 'name', 'category', 'children',
                  'total_lot', 'available_lot')
        read_only_fields = (
            'children', 'total_lot', 'available_lot')

    def to_representation(self, instance):
        representation = super(
            VenueTreeSerializer, self).to_representation(instance)
        representation['children'] = VenueTreeSerializer(
            instance.get_children(), many=True).data
        return representation


class LotPriceSerializer(serializers.ModelSerializer):
    """ """
    class Meta:
        model = models.LotPrice
        fields = (
            'id', 'duration', 'duration_unit', 'pre_paid_amount',
            'amount', 'overdue_amount', 'name')


class VenueViewSerializer(serializers.ModelSerializer):
    """ """
    price = LotPriceSerializer(
        allow_null=True, required=False, source='venue_price')
    total_lot = serializers.IntegerField(default=0, read_only=True)
    available_lot = serializers.IntegerField(default=0, read_only=True)
    location = serializers.CharField(
        max_length=200, allow_null=True, read_only=True,
        allow_blank=True, source='get_location')
    company_name = serializers.CharField(
        max_length=200, allow_null=True, read_only=True,
        allow_blank=True, source='company.name'
    )

    class Meta:
        model = models.Venue
        fields = (
            'id', 'name', 'category', 'price',
            'total_lot', 'available_lot', 'location',
            'company_name')
        read_only_fields = (
            'total_lot', 'available_lot', 'location',
            'company_name')


class VenueSerializer(serializers.ModelSerializer):
    """ """
    price = serializers.PrimaryKeyRelatedField(
        queryset=models.LotPrice.objects.all(),
        allow_null=True, source='venue_price', required=False)
    total_lot = serializers.IntegerField(default=0, read_only=True)
    available_lot = serializers.IntegerField(default=0, read_only=True)
    location = serializers.CharField(
        max_length=200, allow_null=True, allow_blank=True,
        read_only=True, source='get_location')
    company_name = serializers.CharField(
        max_length=200, allow_null=True, read_only=True,
        allow_blank=True, source='company.name'
    )

    class Meta:
        model = models.Venue
        fields = (
            'id', 'name', 'category', 'price', 'venue_type',
            'total_lot', 'available_lot', 'location', 'company_name')
        read_only_fields = ('total_lot', 'available_lot',
                            'location', 'company_name')

    def create(self, validated_data):
        try:
            with transaction.atomic():
                instance = super(
                    VenueSerializer, self).create(validated_data)
                return instance
        except Exception as e:
            raise exceptions.APIException(
                _('Service temporarily unavailable, try again later.')
            )

    def to_representation(self, instance):
        representation = VenueViewSerializer(instance).data
        return representation


class PaymentHistorySerializer(serializers.ModelSerializer):
    """ """
    class Meta:
        model = models.PaymentHistory
        fields = ('id', 'payment_type', 'amount')

    def validate(self, validated_data):
        """ """
        if validated_data.get('reservation'):
            reservation = validated_data['reservation']
            remaining_amount = (
                reservation.total_amount - reservation.total_amount_paid)
            if remaining_amount <= validated_data['amount']:
                raise serializers.ValidationError(
                    _('Total amount to be paid in %s' % (remaining_amount))
                )
        return validated_data

    def create(self, validated_data):
        """ """
        try:
            with transaction.atomic():
                reservation = validated_data['reservation']
                remaining_amount = (
                    reservation.total_amount - reservation.total_amount_paid)
                instance = super(
                    PaymentHistorySerializer, self
                ).create(validated_data)
                if remaining_amount == validated_data['amount']:
                    reservation.payment_status = models.Reservation.FULL_PAID
                elif remaining_amount > validated_data['amount']:
                    reservation.payment_status = models.Reservation.PARTIAL_PAID
                reservation.save()
                return instance
        except Exception as e:
            raise exceptions.APIException(
                _('Service temporarily unavailable, try again later.')
            )


class ReservationVenueSerializer(serializers.ModelSerializer):
    """ """
    class Meta:
        model = models.Venue
        fields = ('id', 'name')


class ReservationViewSerializer(serializers.ModelSerializer):
    """ """
    book_from = TimestampField()
    book_to = TimestampField()
    payments = PaymentHistorySerializer(
        many=True, source='payment_history')
    venue = ReservationVenueSerializer()

    class Meta:
        model = models.Reservation
        fields = (
            'id', 'venue', 'book_from', 'book_to', 'license', 'phone_number',
            'status', 'amount', 'overdue_amount', 'payment_status',
            'total_amount', 'payments', 'user')
        read_only_fields = (
            'amount', 'overdue_amount', 'payment_status',
            'total_amount', 'user')


class ReservationSerializer(ReservationViewSerializer):
    """ """
    book_from = TimestampField()
    book_to = TimestampField()
    venue = serializers.PrimaryKeyRelatedField(
        queryset=models.Venue.objects.all())

    def validate(self, validated_data):
        """ """
        venue = validated_data['venue']
        if validated_data['payment_history']:
            payment = validated_data['payment_history'][0]
        if validated_data['book_from'] > validated_data['book_to']:
            raise serializers.ValidationError(
                _('Reservation end time should be'
                  ' greater than start time')
            )
        check_booking = models.Reservation.objects.filter(
            venue=venue
        ).filter(
            Q(
                book_from__range=(
                    validated_data['book_from'],
                    validated_data['book_to']
                )
            ) |
            Q(
                book_to__range=(
                    validated_data['book_from'],
                    validated_data['book_to']
                )
            )
        )
        if check_booking:
            raise serializers.ValidationError(
                _('Venue not available in given time.'
                  'Please select another slot')
            )

        if venue.venue_price:
            if (
                venue.venue_price.pre_paid_amount
            ) and (
                venue.venue_price.pre_paid_amount < payment['amount']
            ):
                raise serializers.ValidationError(
                    _('Pre paid amount not matched')
                )
        return validated_data

    def update(self, instance, validated_data):
        instance.__dict__.update(**validated_data)
        instance.save()
        return instance

    def create(self, validated_data):
        """
        """
        try:
            with transaction.atomic():
                venue = validated_data['venue']
                payment = validated_data.pop('payment_history')
                if payment:
                    payment = payment[0]
                if venue.venue_price:
                    venue_price = venue.venue_price
                    validated_data['amount'] = venue_price.amount
                    td = (
                        validated_data['book_to'] - validated_data['book_from'])
                    days, hours, minutes = (
                        td.days, td.seconds // 3600, td.seconds // 60 % 60)
                    if venue_price.duration_unit == models.LotPrice.DAY:
                        if hours:
                            days = days + 1
                        total_amount = venue_price.amount * math.ceil(
                            days / venue_price.duration)
                    else:
                        if days:
                            hours = hours + (days * 24)
                        total_amount = venue_price.amount * math.ceil(
                            hours / venue_price.duration
                        )
                    validated_data['total_amount'] = total_amount
                    if validated_data['total_amount'] == payment['amount']:
                        validated_data['payment_status'] = models.Reservation.FULL_PAID
                    elif validated_data['total_amount'] > payment['amount']:
                        validated_data['payment_status'] = models.Reservation.PARTIAL_PAID
                    if payment['amount']:
                        validated_data['total_amount_paid'] = payment['amount']

                instance = super(ReservationSerializer, self).create(
                    validated_data)
                if payment:
                    instance.payment_history.create(**payment)
                return instance
        except Exception as e:
            raise e
            raise exceptions.APIException(
                _('Service temporarily unavailable, try again later.')
            )

    def to_representation(self, instance):
        return ReservationViewSerializer(
            instance, context=self.context
        ).data
