""" parking app view configuration
"""
from django.shortcuts import render
from django.utils.translation import gettext as _


from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from drf_yasg import openapi

from parkinglot import mixins
from . import serializers, models, filters


# Create your views here.
class Login(generics.GenericAPIView):
    """ API endpoint to authenticate and login user.

    All user have to login first to create or book venue
    """
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
        """ API endpoint to authenticate and login user.

        All user have to login first to create or book venue
        """
        serializer = self.serializer_class(
            data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class Detail(generics.GenericAPIView):
    """ """
    serializer_class = serializers.UserDetailSerializer
    model_class = serializer_class.Meta.model

    @swagger_auto_schema(
        operation_id="User Detail",
        tags=['user'],
        responses={
            200: serializers.UserDetailSerializer
        })
    def get(self, request, *args, **kwargs):
        """ API endpoint fetch user detail.
        """
        serializer = self.serializer_class(
            request.user, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="User Update",
        tags=['user'],
        request_body=serializer_class,
        responses={
            200: serializers.UserDetailSerializer
        })
    def put(self, request, *args, **kwargs):
        """ API endpoint fetch user detail.
        """
        serializer = self.serializer_class(
            data=request.data, instance=request.user,
            context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class Register(generics.CreateAPIView):
    """ API endpoint to authenticate & register user detail
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = serializers.RegistrationSerializer
    model_class = serializer_class.Meta.model

    @swagger_auto_schema(
        operation_id="User Registrations",
        tags=['user'],
        request_body=serializer_class,
        responses={
            201: "{'message': 'User generated successfully'}"
        })
    def post(self, request, *args, **kwargs):
        """ API endpoint to authenticate & register user detail
        """
        return self.create(request, *args, **kwargs)


class Company(
        mixins.MultipleFieldLookupMixin, generics.ListCreateAPIView):
    """ API endpoint to list or create company

    User must be logged in to create company.

    Logged in user set as a owner of the company.
    """
    serializer_class = serializers.CompanySerializer
    model_class = serializer_class.Meta.model
    select_related = ()
    prefetch_related = ()
    lookup_fields = ()
    lookup_url_kwargs = ()
    search_fields = ('name',)

    def custom_query_class():
        queryset = self.get_queryset()
        return queryset.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_id="User company list",
        tags=['company'],
        responses={
            200: serializer_class
        }
    )
    def get(self, request, *args, **kwargs):
        """ API endpoint to list all company which logged in user created
        """
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Create new company",
        tags=['company'],
        request_body=serializer_class,
        responses={
            201: serializer_class
        })
    def post(self, request, *args, **kwargs):
        """ API endpoint to create new company

        Active user set as company owner
        """
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CompanyDetail(
        mixins.MultipleFieldLookupMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """ API endpoint to retrieve, update or delete company

    Only owner of the company can perform above operations
    """
    serializer_class = serializers.CompanySerializer
    model_class = serializer_class.Meta.model
    lookup_fields = ('id',)
    lookup_url_kwargs = ('company_id',)
    select_related = ()
    prefetch_related = ()

    def custom_query_class(self):
        queryset = self.get_queryset()
        return queryset.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_id="Company detail",
        tags=['company'],
        responses={
            200: serializer_class
        })
    def get(self, request, *args, **kwargs):
        """ API endpoint to get company detail information"""
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Company Partial Update",
        tags=['company'],
        request_body=serializer_class,
        responses={
            200: serializer_class
        })
    def patch(self, request, *args, **kwargs):
        """ API endpoint to partial update company detail
        """
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Company Update",
        tags=['company'],
        request_body=serializer_class,
        responses={
            200: serializer_class
        })
    def put(self, request, *args, **kwargs):
        """ API endpoint to update company detail"""
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Company Delete",
        tags=['company'],
        request_body=serializer_class,
        responses={
            204: 'NO CONTENT'
        })
    def delete(self, request, *args, **kwargs):
        """ API endpoint to delete company detail"""
        return self.destroy(request, *args, **kwargs)


class LotPrice(
        mixins.MultipleFieldLookupMixin,
        generics.ListCreateAPIView):
    """ API endpoint to create prices for venues
    """
    serializer_class = serializers.LotPriceSerializer
    model_class = serializer_class.Meta.model
    lookup_fields = ('company_id',)
    lookup_url_kwargs = ('company_id',)
    select_related = ()
    prefetch_related = ()
    search_fields = ('name', 'company__name')

    @swagger_auto_schema(
        operation_id="Venue prices",
        tags=['price'],
        responses={
            200: serializer_class
        })
    def get(self, request, *args, **kwargs):
        """ API endpoint to list company prices"""
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Create Venue Price",
        tags=['price'],
        request_body=serializer_class,
        responses={
            201: serializer_class
        })
    def post(self, request, *args, **kwargs):
        """ API endpoint to create new venue price"""
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(company_id=self.kwargs.get('company_id'))


class LotPriceDetail(
        mixins.MultipleFieldLookupMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """  API endpoint to create Retrieve, update or delete venue price
    """
    serializer_class = serializers.LotPriceSerializer
    model_class = serializer_class.Meta.model
    lookup_fields = ('company_id', 'id')
    lookup_url_kwargs = ('company_id', 'lot_price_id')
    select_related = ()
    prefetch_related = ()

    @swagger_auto_schema(
        operation_id="Venue price detail",
        tags=['price'],
        resposes={
            200: serializer_class
        }
    )
    def get(self, request, *args, **kwargs):
        """ API endpoint to get price details"""
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Update venue price detail",
        tags=['price'],
        resposes={
            200: serializer_class
        }
    )
    def put(self, request, *args, **kwargs):
        """ API endpoint to update price detail"""
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Partial update venue price detail",
        tags=['price'],
        resposes={
            200: serializer_class
        }
    )
    def patch(self, request, *args, **kwargs):
        """ API endpoint to partial update price detail"""
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Delete venue price detail",
        tags=['price'],
        resposes={
            204: 'NO CONTENT'
        }
    )
    def delete(self, request, *args, **kwargs):
        """ API endpoint to delete price detail

        On price delete all the relation with venue will set null
        """
        return self.destroy(request, *args, **kwargs)


class VenueTree(
        mixins.MultipleFieldLookupMixin,
        generics.ListCreateAPIView):
    """ API endpoint to get tree view for company

    Venue tree only visible if venue have parent child relation ship
    """
    serializer_class = serializers.VenueTreeSerializer
    model_class = serializer_class.Meta.model
    authentication_classes = ()
    permission_classes = ()
    lookup_fields = ('company_id',)
    lookup_url_kwargs = ('company_id',)
    search_fields = ('name', 'company__name', 'parent__name')

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
        """ API endpoint to get venue tree view

        Venue tree only visible if venue have parent child relation ship
        """
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
    """ API endpoint to get or create Venue"""
    serializer_class = serializers.VenueTreeSerializer
    model_class = serializer_class.Meta.model
    authentication_classes = ()
    permission_classes = ()
    lookup_fields = ('parent_id',)
    lookup_url_kwargs = ('venue_id',)
    search_fields = ('name', 'parent__name', 'company__name')
    filter_class = filters.VenueFilter

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
        """ API endpoint to list all venues based venue id"""
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Create Sub Venue",
        tags=['venue'],
        request_body=serializers.VenueSerializer,
        responses={
            200: serializers.VenueViewSerializer
        }
    )
    def post(self, request, *args, **kwargs):
        """ API endpoint to create new sub venue

        URL venue id set as a parent id for newly created venue
        """
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(parent_id=self.kwargs.get('venue_id'))


class VenueDetail(
        mixins.MultipleFieldLookupMixin,
        generics.RetrieveUpdateDestroyAPIView):
    """ API endpoint to retrieve, update and delete venue

    On venue delete all the reservation get deleted
    """
    serializer_class = serializers.VenueSerializer
    model_class = serializer_class.Meta.model
    select_related = ()
    prefetch_related = ()
    lookup_fields = ('id',)
    lookup_url_kwargs = ('venue_id',)

    @swagger_auto_schema(
        operation_id="Venue Detail",
        tags=['venue'],
        responses={
            200: serializers.VenueViewSerializer
        }
    )
    def get(self, request, *args, **kwargs):
        """ API endpoint to get venue detail"""
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Update Venue Detail",
        tags=['venue'],
        request_body=serializers.VenueSerializer,
        responses={
            200: serializers.VenueViewSerializer
        }
    )
    def put(self, request, *args, **kwargs):
        """ API endpoint to update venue detail"""
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Partial Update Venue Detail",
        tags=['venue'],
        request_body=serializers.VenueSerializer,
        responses={
            200: serializers.VenueViewSerializer
        }
    )
    def patch(self, request, *args, **kwargs):
        """ API endpoint to partial update venue detail"""
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Delete Venue Detail",
        tags=['venue'],
        request_body=serializers.VenueSerializer,
        responses={
            204: "NO CONTENT"
        }
    )
    def delete(self, request, *args, **kwargs):
        """ API endpoint to delete venue detail"""
        return self.destroy(request, *args, **kwargs)


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

    def custom_query_class(self):
        """ """
        queryset = self.get_queryset()
        return queryset.filter(
            category=self.model_class.LOT,
            venue_type=self.model_class.PUBLIC)

    @swagger_auto_schema(
        operation_id="Search Venue detail",
        tags=['venue'],
        responses={
            200: serializers.VenueSerializer
        }
    )
    def get(self, request, *args, **kwargs):
        """ API endpoint to search venues from all company
        """
        return self.list(request, *args, **kwargs)


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

    def custom_query_class(self):
        queryset = self.get_queryset()
        return queryset.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_id="List user reservation",
        tags=['reservation'],
        responses={
            200: serializers.ReservationViewSerializer
        }
    )
    def get(self, request, *args, **kwargs):
        """ API endpoint to get reservation list
        """
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Create new reservation",
        tags=['reservation'],
        responses={
            200: serializers.ReservationViewSerializer
        }
    )
    def post(self, request, *args, **kwargs):
        """ API endpoint to create new user reservation
        """
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CompanyReservationList(ReservationList):
    """ API endpoint to get venue reservation list
    """

    def custom_query_class(self):
        queryset = self.get_queryset()
        return queryset.filter(
            venue__company__user=self.request.user
        )


class ReservationDetail(
        mixins.MultipleFieldLookupMixin,
        generics.RetrieveUpdateAPIView):
    """ API endpoint to get or update reservation detail"""
    serializer_class = serializers.ReservationSerializer
    model_class = serializer_class.Meta.model
    select_related = ()
    prefetch_related = ()
    lookup_fields = ('id', )
    lookup_url_kwargs = ('reservation_id',)
    filter_class = filters.ReservationFilter
    search_fields = ('venue__name',)

    @swagger_auto_schema(
        operation_id="Reservation detail",
        tags=['reservation'],
        responses={
            200: serializers.ReservationViewSerializer
        }
    )
    def get(self, request, *args, **kwargs):
        """ API endpoint to get reservation detail"""
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Partial update Reservation",
        tags=['reservation'],
        responses={
            200: serializers.ReservationViewSerializer
        }
    )
    def patch(self, request, *args, **kwargs):
        """ API endpoint to get reservation detail"""
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Update Reservation",
        tags=['reservation'],
        responses={
            200: serializers.ReservationViewSerializer
        }
    )
    def put(self, request, *args, **kwargs):
        """ API endpoint to get reservation detail"""
        return self.update(request, *args, **kwargs)


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

    @swagger_auto_schema(
        operation_id="Reservation payment list",
        tags=['payment'],
        responses={
            200: serializers.PaymentHistorySerializer
        }
    )
    def get(self, request, *args, **kwargs):
        """ API endpoint to fetch payment detail for reservation"""
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="Create new reservation payment",
        tags=['payment'],
        responses={
            200: serializers.PaymentHistorySerializer
        }
    )
    def post(self, request, *args, **kwargs):
        """ API endpoint to create new payment record for reservation"""
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(
            Reservation_id=self.kwargs.get('reservation_id'))
