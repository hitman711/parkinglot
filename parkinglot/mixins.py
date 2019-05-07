import logging
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Permission

from rest_framework.response import Response

logs = logging.getLogger(__name__)

class MultipleFieldLookupMixin(object):
    """
    View mixins to perform filter operation on model for
    retrieve data based on lookup field
    Parameters
    ----------
    lookup_fields : Tuple
        List of model parameters or search parameter
    lookup_url_kwargs : Tuple
        List of search data received from url to filter model information
      note :: Both lookup_fields, lookup_url_kwargs related to each other
        (i.e. In filter `lookup_fields` act as Key & `lookup_url_kwargs` act
        as Value)
    """

    def get_queryset(self, *args, **kwargs):
        """ Generate basic queryset based on URL view
            `select_related`, `prefetch_related` parameter pass from
            APIView
        """
        queryset = self.model_class.objects
        try:
            if self.select_related:
                queryset = queryset.select_related(*self.select_related)
            if self.prefetch_related:
                queryset = queryset.prefetch_related(*self.prefetch_related)
        except Exception as e:
            logs.info(e)
        return queryset

    def get_object(self):
        """ Return single object
        """
        try:
            queryset = self.custom_query_class()
        except Exception as e:
            logs.info(e)
            queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        filter = {}
        # Field out `lookup_fields` and `lookup_url_kwargs` fields
        for field in self.lookup_fields:
            filter[field] = self.kwargs[
                self.lookup_url_kwargs[
                    self.lookup_fields.index(field)
                ]
            ]
        return get_object_or_404(queryset, **filter)

    def custom_lookup_filter(self, queryset):
        """ Add Filter value in queryset based on `lookup_fields` &
        `lookup_url_kwargs` fields
        """
        filter = {}
        for field in self.lookup_fields:
            filter[field] = self.kwargs[
                self.lookup_url_kwargs[
                    self.lookup_fields.index(field)
                ]
            ]
        return queryset.filter(**filter)

    def list(self, *args, **kwargs):
        """ Return list objects based on queryset
        """
        try:
            queryset = self.filter_queryset(self.custom_query_class())
        except Exception as e:
            logs.info(e)
            queryset = self.filter_queryset(self.get_queryset())
        queryset = self.custom_lookup_filter(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DynamicFieldsMixin(object):
    """
    View mixins to filter specific fields from model
    retrieve specific data based on field list
    """

    @property
    def fields(self):
        """
        Filters the fields according to the `fields` query parameter.
        A blank `fields` parameter (?fields) will remove all fields. Not
        passing `fields` will pass all fields individual fields are comma
        separated (?fields=id,name,url,email).
        """
        fields = super(DynamicFieldsMixin, self).fields
        if not hasattr(self, '_context'):
            # We are being called before a request cycle
            return fields

        # Only filter if this is the root serializer, or if the parent is the
        # root serializer with many=True
        is_root = self.root == self
        parent_is_list_root = self.parent == self.root and getattr(
            self.parent, 'many', False)
        if not (is_root or parent_is_list_root):
            return fields

        try:
            request = self.context['request']
        except KeyError:
            warnings.warn('Context does not have access to request')
            return fields

        # NOTE: drf test framework builds a request object where the query
        # parameters are found under the GET attribute.
        params = getattr(
            request, 'query_params', getattr(request, 'GET', None)
        )
        if params is None:
            warnings.warn('Request object does not contain query paramters')

        try:
            filter_fields = params.get('fields', None).split(',')
        except AttributeError:
            filter_fields = None

        try:
            omit_fields = params.get('omit', None).split(',')
        except AttributeError:
            omit_fields = []

        # Drop any fields that are not specified in the `fields` argument.
        existing = set(fields.keys())
        if filter_fields is None:
            # no fields param given, don't filter.
            allowed = existing
        else:
            allowed = set(filter(None, filter_fields))

        # omit fields in the `omit` argument.
        omitted = set(filter(None, omit_fields))

        for field in existing:

            if field not in allowed:
                fields.pop(field, None)

            if field in omitted:
                fields.pop(field, None)

        return fields
