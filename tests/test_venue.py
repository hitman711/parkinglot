import json
import pytest
import urllib
import http.client
from dateutil.relativedelta import relativedelta
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from django.urls import reverse
from parking.models import (
    Company, Venue, LotPrice, Reservation, PaymentHistory)

from .fixtures.test_fixtures import (
    TokenFactory, CompanyFactory, BuildingVenueFactory,
    FloorVenueFactory, LotFactory, PriceFactory,
    UserFactory)
from parking.models import Venue


@pytest.mark.django_db
class TestCompanyAPI(object):

    @pytest.fixture(autouse=True)
    def setup(self, client, user_token, user_company):
        self.client = client
        self.login_key = [
            'id', 'first_name', 'last_name', 'username',
            'email', 'authentication_code'
        ].sort()
        self.company_key = [
            'id', 'name', 'total_lot', 'available_lot'
        ].sort()
        self.venue_key = [
            'id', 'name', 'category', 'children',
            'total_lot', 'available_lot'
        ].sort()
        self.list_key = ['count', 'next', 'previous', 'results'].sort()
        self.price_key = [
            'id', 'name', 'duration', 'duration_unit',
            'pre_paid_amount', 'amount', 'overdue_amount'].sort()
        self.user = user_token.user
        self.token = user_token.key

    def test_venue_tree(self, client):
        """ """
        company = CompanyFactory(user=self.user, name='Company 1')
        BuildingVenueFactory(company=company, name='Buiding 1')

        response = self.client.get(
            reverse(
                'venue-tree',
                kwargs={
                    'version': 1,
                    'company_id': company.id
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Token %s' % (self.token)
        )
        assert response.status_code == 200
        json_response = response.json()
        list_key = list(json_response.keys())
        assert self.list_key == list_key.sort()
        for x in json_response['results']:
            venue_key = list(x.keys())
            assert self.venue_key == venue_key.sort()

    def test_list_price(self, client):
        """ """
        company = CompanyFactory(user=self.user, name='Company 1')
        LotFactory(company=company, name='Parking 1', parent=None)
        LotFactory(company=company, name='Parking 2', parent=None)

        response = self.client.get(
            reverse(
                'company-detail',
                kwargs={
                    'version': 1,
                    'company_id': company.id
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Token %s' % (self.token)
        )
        assert response.status_code == 200
        json_response = response.json()
        company_key = list(json_response.keys())
        self.company_key = company_key.sort()
        assert json_response['total_lot'] == 2
        assert json_response['available_lot'] == 2

    def test_complex_structure(self, client, user_company):
        """ """
        company = user_company
        for building in range(1, 10):
            build = BuildingVenueFactory(
                company=company, name='Building %s' % (building))
            for floor in range(1, 4):
                each_floor = FloorVenueFactory(
                    parent=build, name='Floor %s' % (floor),
                    category=Venue.FLOOR)
                for lot in range(1, 10):
                    LotFactory(
                        parent=each_floor,
                        name='Parking %s' % (each_floor))

        response = self.client.get(
            reverse(
                'venue-tree',
                kwargs={
                    'version': 1,
                    'company_id': company.id
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Token %s' % (self.token)
        )
        assert response.status_code == 200
        json_response = response.json()
        list_key = list(json_response.keys())
        assert self.list_key == list_key.sort()
        for x in json_response['results']:
            venue_key = list(x.keys())
            assert self.venue_key == venue_key.sort()
            assert x['category'] in [Venue.BUILDING, Venue.FLOOR, Venue.LOT]
            for y in x['children']:
                venue_key = list(y.keys())
                assert self.venue_key == venue_key.sort()
                assert y['category'] in [
                    Venue.BUILDING, Venue.FLOOR, Venue.LOT]
                for z in y['children']:
                    venue_key = list(z.keys())
                    assert self.venue_key == venue_key.sort()
                    assert z['category'] in [
                        Venue.BUILDING, Venue.FLOOR, Venue.LOT]

    def test_list_get_rate(self, client, user_company):
        """ """
        company = user_company
        response = self.client.get(
            reverse(
                'lot-price',
                kwargs={
                    'version': 1,
                    'company_id': company.id
                },
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Token %s' % (self.token)
        )
        assert response.status_code == 200
        json_response = response.json()
        list_key = list(json_response.keys())
        self.list_key == list_key.sort()
        assert not json_response['results']

    def test_create_rate(self, client, user_company):
        """ """
        company = user_company
        json_data = {
            'name': 'Car rate',
            'duration': 1,
            'duration_unit': LotPrice.HOUR,
            'pre_paid_amount': '10.00',
            'amount': '100',
            'overdue_amount': '5.00'
        }
        response = self.client.post(
            reverse(
                'lot-price',
                kwargs={
                    'version': 1,
                    'company_id': company.id
                },
            ),
            data=json.dumps(json_data),
            content_type='application/json',
            HTTP_AUTHORIZATION='Token %s' % (self.token)
        )
        assert response.status_code == 201
        json_response = response.json()
        price_key = list(json_response.keys())
        assert self.price_key == price_key.sort()

    def test_create_venue_with_price(self, client, user_company):
        """ """
        company = user_company
        company_price = PriceFactory(
            duration=1,
            duration_unit=LotPrice.HOUR,
            company=company,
            pre_paid_amount=10,
            amount=100,
            overdue_amount=5
        )
        json_data = {
            'name': 'Parking 1',
            'price': company_price.id,
            'category': Venue.LOT
        }

        response = self.client.post(
            reverse(
                'venue-tree',
                kwargs={
                    'version': 1,
                    'company_id': company.id
                }
            ),
            data=json.dumps(json_data),
            content_type='application/json',
            HTTP_AUTHORIZATION='Token %s' % (self.token)
        )
        assert response.status_code == 201
        json_resopnse = response.json()
        venue_key = list(json_resopnse.keys())
        self.venue_key == venue_key.sort()
        price_key = list(json_resopnse['price'].keys())
        self.price_key == price_key.sort()

    def test_create_sub_venue_with_price(self, client, user_company):
        """ """
        company = user_company
        building_venue = BuildingVenueFactory(
            name='Building 1', category=Venue.BUILDING,
            company=company
        )
        company_price = PriceFactory(
            duration=1,
            duration_unit=LotPrice.HOUR,
            company=company,
            pre_paid_amount=10,
            amount=100,
            overdue_amount=5
        )
        json_data = {
            'name': 'Parking 1',
            'price': company_price.id,
            'category': Venue.LOT
        }

        response = self.client.post(
            reverse(
                'sub-venue-list',
                kwargs={
                    'version': 1,
                    'venue_id': building_venue.id
                }
            ),
            data=json.dumps(json_data),
            content_type='application/json',
            HTTP_AUTHORIZATION='Token %s' % (self.token)
        )
        assert response.status_code == 201
        json_resopnse = response.json()
        venue_key = list(json_resopnse.keys())
        self.venue_key == venue_key.sort()
        price_key = list(json_resopnse['price'].keys())
        self.price_key == price_key.sort()


@pytest.mark.django_db
class TestReservationAPI(object):

    @pytest.fixture(autouse=True)
    def setup(self, client, user_token, user_company):
        self.client = client
        self.login_key = [
            'id', 'first_name', 'last_name', 'username',
            'email', 'authentication_code'
        ].sort()
        self.company_key = [
            'id', 'name', 'total_lot', 'available_lot'
        ].sort()
        self.venue_key = [
            'id', 'name', 'category', 'children',
            'total_lot', 'available_lot'
        ].sort()
        self.list_key = ['count', 'next', 'previous', 'results'].sort()
        self.price_key = [
            'id', 'name', 'duration', 'duration_unit',
            'pre_paid_amount', 'amount', 'overdue_amount'].sort()
        self.reservation_key = [
            'id', 'book_from', 'book_to', 'license', 'phone_number',
            'status', 'amount', 'overdue_amount', 'payment_status',
            'total_amount', 'payments', 'user'
        ].sort()
        self.payment_key = ['id', 'amount', 'payment_type']
        self.user = user_token.user
        self.token = user_token.key
        self.company = user_company

    def test_create_reservation_data(self, client):
        """ """
        new_user = UserFactory(
            username='ganesh',
            password=make_password('sidh@123'),
            first_name='Ganesh', last_name='Gore',
            email='gane123@gmail.com')
        token = TokenFactory(user=new_user)
        price = PriceFactory(
            name='Car price', company=self.company,
            duration=1, duration_unit=LotPrice.HOUR,
            pre_paid_amount=10, amount=100, overdue_amount=5)

        for x in range(1, 10):
            LotFactory(
                company=self.company,
                name='Parking %s' % (x),
                venue_price=price,
                parent=None)

        book_from = int(timezone.now().strftime('%s'))
        book_to = int((timezone.now() + relativedelta(hours=2)).strftime('%s'))

        json_data = {
            'venue': 1,
            'book_from': book_from,
            'book_to': book_to,
            'payments': [{
                'amount': 10,
                'payment_type': PaymentHistory.CASH
            }],
            'license': 'MH 04 1234',
            'phone_number': '+918082611337'
        }
        response = self.client.post(
            reverse(
                'reservation',
                kwargs={
                    'version': 1
                }
            ),
            data=json.dumps(json_data),
            content_type='application/json',
            HTTP_AUTHORIZATION='Token %s' % (token.key)
        )
        assert response.status_code == 201
        json_response = response.json()
        reservation_key = list(json_response.keys())
        assert self.reservation_key == reservation_key.sort()
        assert json_response['status'] == Reservation.PENDING
        assert json_response['payment_status'] == Reservation.PARTIAL_PAID
        assert json_response['book_from'] == book_from
        assert json_response['book_to'] == book_to
        for x in json_response['payments']:
            for keys in self.payment_key:
                assert x[keys]

    def test_invalid_parameter_in_reservation(self, client):
        new_user = UserFactory(
            username='ganesh',
            password=make_password('sidh@123'),
            first_name='Ganesh', last_name='Gore',
            email='gane123@gmail.com')
        token = TokenFactory(user=new_user)
        price = PriceFactory(
            name='Car price', company=self.company,
            duration=1, duration_unit=LotPrice.HOUR,
            pre_paid_amount=10, amount=100, overdue_amount=5)

        for x in range(1, 10):
            LotFactory(
                company=self.company,
                name='Parking %s' % (x),
                venue_price=price,
                parent=None)

        book_from = int(timezone.now().strftime('%s'))
        book_to = int((timezone.now() + relativedelta(hours=2)).strftime('%s'))

        json_data = {
            'venue': 1,
            # 'book_from': book_from,
            # 'book_to': book_to,
            'payments': [{
                'amount': 10,
                'payment_type': PaymentHistory.CASH
            }],
            'license': 'MH 04 1234',
            'phone_number': '+918082611337'
        }
        response = self.client.post(
            reverse(
                'reservation',
                kwargs={
                    'version': 1
                }
            ),
            data=json.dumps(json_data),
            content_type='application/json',
            HTTP_AUTHORIZATION='Token %s' % (token.key)
        )
        assert response.status_code == 400
        json_response = response.json()
        assert json_response['book_from']
        assert json_response['book_to']

    def test_reservation_on_same_date(self, client):
        new_user = UserFactory(
            username='ganesh',
            password=make_password('sidh@123'),
            first_name='Ganesh', last_name='Gore',
            email='gane123@gmail.com')
        token = TokenFactory(user=new_user)
        price = PriceFactory(
            name='Car price', company=self.company,
            duration=1, duration_unit=LotPrice.HOUR,
            pre_paid_amount=10, amount=100, overdue_amount=5)

        for x in range(1, 10):
            LotFactory(
                company=self.company,
                name='Parking %s' % (x),
                venue_price=price,
                parent=None)

        book_from = int(timezone.now().strftime('%s'))
        book_to = int((timezone.now() + relativedelta(hours=2)).strftime('%s'))

        json_data = {
            'venue': 1,
            'book_from': book_from,
            'book_to': book_to,
            'payments': [{
                'amount': 10,
                'payment_type': PaymentHistory.CASH
            }],
            'license': 'MH 04 1234',
            'phone_number': '+918082611337'
        }
        response = self.client.post(
            reverse(
                'reservation',
                kwargs={
                    'version': 1
                }
            ),
            data=json.dumps(json_data),
            content_type='application/json',
            HTTP_AUTHORIZATION='Token %s' % (token.key)
        )
        assert response.status_code == 201

        json_data = {
            'venue': 1,
            'book_from': book_from,
            'book_to': book_to,
            'payments': [{
                'amount': 10,
                'payment_type': PaymentHistory.CASH
            }],
            'license': 'MH 04 1234',
            'phone_number': '+918082611337'
        }
        response = self.client.post(
            reverse(
                'reservation',
                kwargs={
                    'version': 1
                }
            ),
            data=json.dumps(json_data),
            content_type='application/json',
            HTTP_AUTHORIZATION='Token %s' % (token.key)
        )
        assert response.status_code == 400
        json_response = response.json()
        assert json_response['non_field_errors']


    def test_reservation_invalid_date_format(self, client):
        new_user = UserFactory(
            username='ganesh',
            password=make_password('sidh@123'),
            first_name='Ganesh', last_name='Gore',
            email='gane123@gmail.com')
        token = TokenFactory(user=new_user)
        price = PriceFactory(
            name='Car price', company=self.company,
            duration=1, duration_unit=LotPrice.HOUR,
            pre_paid_amount=10, amount=100, overdue_amount=5)

        for x in range(1, 10):
            LotFactory(
                company=self.company,
                name='Parking %s' % (x),
                venue_price=price,
                parent=None)

        book_from = str(timezone.now())
        book_to = str(timezone.now())

        json_data = {
            'venue': 1,
            'book_from': book_from,
            'book_to': book_to,
            'payments': [{
                'amount': 10,
                'payment_type': PaymentHistory.CASH
            }],
            'license': 'MH 04 1234',
            'phone_number': '+918082611337'
        }
        response = self.client.post(
            reverse(
                'reservation',
                kwargs={
                    'version': 1
                }
            ),
            data=json.dumps(json_data),
            content_type='application/json',
            HTTP_AUTHORIZATION='Token %s' % (token.key)
        )
        assert response.status_code == 400
        json_response = response.json()
        assert json_response['book_from']
        assert json_response['book_to']