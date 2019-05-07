from django.urls import path
from . import views

urlpatterns = [
    path('login', views.Login.as_view(), name='login'),
    path('register', views.Register.as_view(), name='register'),
    path('company', views.Company.as_view(), name='company'),
    path('company/<int:company_id>', views.CompanyDetail.as_view(), 
        name='company-detail'),
    path('company/<int:company_id>/price', 
        views.LotPrice.as_view(), name='lot-price'),
    path('company/<int:company_id>/price/<int:lot_price_id>', 
        views.LotPriceDetail.as_view(), name='lot-price'),
    path('company/<int:company_id>/venue', views.VenueTree.as_view(), 
        name='venue-tree'),
    path('venue/<int:venue_id>/venue', views.Venue.as_view(), name='sub-venue-list'),
    path('venue/<int:venue_id>', views.VenueDetail.as_view(), name='venue-detail'),
    path('venue', views.VenueList.as_view(), name='venue'),
    path('reservation', views.ReservationList.as_view(), name='reservation'),
    path('reservation/<int:reservation_id>/payment', 
        views.PaymentHistory.as_view(), name='payment')
]