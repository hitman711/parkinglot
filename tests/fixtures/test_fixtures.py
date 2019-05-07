import pytest
import factory
from pytest_factoryboy import register

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token

from parking.models import Company, Venue, LotPrice

@register
class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = User

    username = "sidh711"
    password = make_password('sidh@123') 
    first_name = 'Siddhesh'
    last_name = 'Gore'
    email = 'sidh711@gmail.com'

register(UserFactory, "user")

@register
class TokenFactory(factory.DjangoModelFactory):

    class Meta:
        model = Token
    
    user = factory.SubFactory(UserFactory)

register(TokenFactory, 'user_token')

@pytest.mark.django_db
def test_model_fixture(user):
    assert user.username == "sidh711"

@register
class CompanyFactory(factory.DjangoModelFactory):
    
    class Meta:
        model = Company
    
    name = 'Company 1'
    user = factory.SubFactory(UserFactory)

register(CompanyFactory, 'user_company')

@pytest.mark.django_db
def test_company_model_fixture(user_company):
    assert user_company.name == "Company 1"

@register
class BuildingVenueFactory(factory.DjangoModelFactory):

    class Meta:
        model = Venue
    
    name = 'Building 1'
    company = factory.SubFactory(CompanyFactory)
    category = Venue.BUILDING
    parent = None

register(BuildingVenueFactory, 'building_venue')

@pytest.mark.django_db
def test_building_model_fixture(building_venue):
    assert building_venue.name == "Building 1"

@register
class FloorVenueFactory(factory.DjangoModelFactory):

    class Meta:
        model = Venue
    
    name = 'Floor 1'
    company = None
    category = Venue.FLOOR
    parent = factory.SubFactory(CompanyFactory)

register(FloorVenueFactory, 'floor_venue')

# @pytest.mark.django_db
# def test_floor_model_fixture(floor_venue):
#     assert floor_venue.name == "Building 1"

@register
class LotFactory(factory.DjangoModelFactory):

    class Meta:
        model = Venue
    
    name = 'Lot 1'
    company = None
    category = Venue.LOT
    parent = factory.SubFactory(FloorVenueFactory)

register(LotFactory, 'floor_venue')

@register
class PriceFactory(factory.DjangoModelFactory):
    
    class Meta:
        model = LotPrice

    name = 'Car price'
    company = factory.SubFactory(CompanyFactory)
    duration = 1
    duration_unit = LotPrice.HOUR
    amount = 100
    pre_paid_amount = 20
    overdue_amount = 10

register(PriceFactory, 'company_price')

@pytest.mark.django_db
def test_price_model_fixture(company_price):
    assert company_price.name == "Car price"