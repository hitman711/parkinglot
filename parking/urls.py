""" parking app URL configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    # User login
    path('login', views.Login.as_view(), name='login'),
    # User registration 
    path('register', views.Register.as_view(), name='register'),
    # User company list
    path('company', views.Company.as_view(), name='company'),
    # Company detail
    path('company/<int:company_id>', views.CompanyDetail.as_view(), 
        name='company-detail'),
    # Company venue price list
    path('company/<int:company_id>/price', 
        views.LotPrice.as_view(), name='lot-price'),
    # Price detail
    path('company/<int:company_id>/price/<int:lot_price_id>', 
        views.LotPriceDetail.as_view(), name='lot-price'),
    # Company venue tree
    path('company/<int:company_id>/venue', views.VenueTree.as_view(), 
        name='venue-tree'),
    # Company sub venue list
    path('venue/<int:venue_id>/venue', views.Venue.as_view(), name='sub-venue-list'),
    # Company venue detail
    path('venue/<int:venue_id>', views.VenueDetail.as_view(), name='venue-detail'),
    # Check venue availability
    path('venue/<int:venue_id>', views.VenueAvailable.as_view(), name='venue-available'),
    # Venue search from all company
    path('venue', views.VenueList.as_view(), name='venue'),
    # Venue booking
    path('reservation', views.ReservationList.as_view(), name='reservation'),
    # Venue booking payment
    path('reservation/<int:reservation_id>/payment', 
        views.PaymentHistory.as_view(), name='payment')
]