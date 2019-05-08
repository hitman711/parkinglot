"""parkinglot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

description = "Parkinglot application provide solution to the user to find" \
"parking place near to them. Also for the user to create & manage parking " \
"places. User can create there own company or place and add parking place in" \
" in that, set price for each parking place with duration and pre paid charges." \
"User search places near to him, find available parkinglot, reserve the " \
"parking place by paying pre paid amount and it's done. Once user park his" \
" vehicle on parking spot then reservation will set active. When user remove his" \
" vehicle from parking spot then reservation set closed. Before marked as closed" \
" total payment calculate based on duration user selected for parking and over due" \
" charges(in case of over due)."

schema_view = get_schema_view(
   openapi.Info(
      title="Parking plot API",
      default_version='v1',
      description=description
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('v<int:version>/', include('parking.urls'), name='Parking urls'),
#    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
#    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
