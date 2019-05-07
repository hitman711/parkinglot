from django.shortcuts import render

from rest_framework import generics, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from parkinglot import mixins
from . import serializers, models, filters


# Create your views here.
class Login(generics.GenericAPIView):
    """ """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.UserLoginSerializer
    model_class = serializer_class.Meta.model

    @swagger_auto_schema(
        operation_id="User login", 
        tags=['user'],
        request_body=serializer_class,
        responses={
            200: serializers.UserDetailSerializer
        })
    def post(self, request, *args, **kwargs):
        """ API endpoint to logged in user"""
        serializer = self.serializer_class(
            data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class Register(generics.GenericAPIView):
    """ """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.RegistrationSerializer
    model_class = serializer_class.Meta.model


class Company(
    mixins.MultipleFieldLookupMixin, generics.ListCreateAPIView):
    serializer_class = serializers.CompanySerializer
    model_class = serializer_class.Meta.model
    select_related = ()
    prefetch_related = ()
    lookup_fields = ()
    lookup_url_kwargs = ()
    search_fields = ('name',)

    @swagger_auto_schema(
        operation_id="User company list", 
        tags=['company']
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Create new company", 
        tags=['company'],
        request_body=serializer_class,
        responses={
            201: serializer_class
        })
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CompanyDetail(
    mixins.MultipleFieldLookupMixin, 
    generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.CompanySerializer
    model_class = serializer_class.Meta.model
    lookup_fields = ('id',)
    lookup_url_kwargs = ('company_id',)
    select_related = ()
    prefetch_related = ()

class LotPrice(
    mixins.MultipleFieldLookupMixin,
    generics.ListCreateAPIView):
    serializer_class = serializers.LotPriceSerializer
    model_class = serializer_class.Meta.model
    lookup_fields = ('company_id',)
    lookup_url_kwargs = ('company_id',)
    select_related = ()
    prefetch_related = ()

    @swagger_auto_schema(
        operation_id="Lot price list", 
        tags=['venue_price']
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Create new price", 
        tags=['venue_price'],
        request_body=serializer_class,
        responses={
            201: serializer_class
        })
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(company_id=self.kwargs.get('company_id'))

class LotPriceDetail(
    mixins.MultipleFieldLookupMixin,
    generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.LotPriceSerializer
    model_class = serializer_class.Meta.model
    lookup_fields = ('company_id', 'id')
    lookup_url_kwargs = ('company_id', 'lot_price_id')
    select_related = ()
    prefetch_related = ()

    @swagger_auto_schema(
        operation_id="Venue price detail", 
        tags=['venue_price'],
        resposes={
            200: serializer_class
        }
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Update venue price detail", 
        tags=['venue_price'],
        resposes={
            200: serializer_class
        }
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Partial update venue price detail", 
        tags=['venue_price'],
        resposes={
            200: serializer_class
        }
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Delete venue price detail", 
        tags=['venue_price'],
        resposes={
            204: 'NO CONTENT'
        }
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class VenueTree(
    mixins.MultipleFieldLookupMixin,
    generics.ListCreateAPIView):
    """ """
    serializer_class = serializers.VenueTreeSerializer
    model_class = serializer_class.Meta.model
    authentication_classes = ()
    permission_classes = ()
    lookup_fields = ('company_id',)
    lookup_url_kwargs = ('company_id',)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.VenueSerializer
        else:
            return serializers.VenueTreeSerializer

    @swagger_auto_schema(
        operation_id="Company venue list", 
        tags=['venue'],
        responses={
            200: serializers.VenueTreeSerializer
        })
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_id="Create company", 
        tags=['venue'],
        request_body=serializers.VenueSerializer,
        responses={
            201: serializers.VenueSerializer
        })
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(company_id=self.kwargs.get('company_id'))
        
class Venue(mixins.MultipleFieldLookupMixin, generics.ListCreateAPIView):
    serializer_class = serializers.VenueTreeSerializer
    model_class = serializer_class.Meta.model
    authentication_classes = ()
    permission_classes = ()
    lookup_fields = ('parent_id',)
    lookup_url_kwargs = ('venue_id',)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.VenueSerializer
        else:
            return serializers.VenueTreeSerializer

    @swagger_auto_schema(
        operation_id="Sub venue list", 
        tags=['venue'],
        responses={
            200: serializers.VenueTreeSerializer
        })
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_id="Create sub venue", 
        tags=['venue'],
        request_body=serializers.VenueSerializer,
        responses={
            201: serializers.VenueViewSerializer,
        }
    )

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(parent_id=self.kwargs.get('venue_id'))


class VenueDetail(
    mixins.MultipleFieldLookupMixin, 
    generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.VenueSerializer
    model_class = serializer_class.Meta.model
    select_related = ()
    prefetch_related = ()
    lookup_fields = ('id',)
    lookup_url_kwargs = ('venue_id',)

class VenueList(
    mixins.MultipleFieldLookupMixin,
    generics.ListAPIView):
    serializer_class = serializers.VenueSerializer
    model_class = serializer_class.Meta.model
    select_related = ()
    prefetch_related = ()
    lookup_fields = ()
    lookup_url_kwargs = ()
    filter_class = filters.VenueFilter
    search_fields = ('name', 'company__name', 'parent__name')

class ReservationList(
    mixins.MultipleFieldLookupMixin,
    generics.ListCreateAPIView):
    serializer_class = serializers.ReservationSerializer
    model_class = serializer_class.Meta.model
    select_related = ()
    prefetch_related = ()
    lookup_fields = ()
    lookup_url_kwargs = ()
    filter_class = filters.ReservationFilter
    search_fields = ('venue__name',)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PaymentHistory(
    mixins.MultipleFieldLookupMixin,
    generics.ListCreateAPIView
):
    serializer_class = serializers.PaymentHistorySerializer
    model_class = serializer_class.Meta.model
    select_related = ('reservation',)
    prefetch_related = ()
    lookup_fields = ('reservation_id',)
    lookup_url_kwargs = ('reservation_id',)

    def perform_create(self, serializer):
        serializer.save(
            Reservation_id=self.kwargs.get('reservation_id'))