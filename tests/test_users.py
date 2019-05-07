import json
import pytest
import urllib
import http.client

from django.urls import reverse

from .fixtures.test_fixtures import CompanyFactory

@pytest.mark.django_db
class TestUserAPI(object):
    
    @pytest.fixture(autouse=True)
    def setup(self, client, user):
        self.client = client
        self.login_key = [
            'id', 'first_name', 'last_name', 'username',
            'email', 'authentication_code'
        ].sort()
        self.company_key = [
            'id', 'name', 'total_lot', 'available_lot'
        ].sort()
        self.list_key = ['count', 'next', 'previous', 'results'].sort()
        self.user = None
        self.token = None
    
    def test_login(self):
        """ """
        json_data = {
            'username': 'sidh711',
            'password': 'sidh@123'
        }
        response = self.client.post(
            reverse(
                'login',
                kwargs={'version': 1}
            ),
            data=json.dumps(json_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        json_response = response.json()
        login_key = list(json_response.keys())
        assert self.login_key == login_key.sort()

    def test_company(self, user_token):
        """ """
        json_data = {
            'name': 'Company private'
        }
        response = self.client.post(
            reverse(
                'company',
                kwargs={'version':1},
            ),
            data=json.dumps(json_data),
            content_type='application/json',
            HTTP_AUTHORIZATION='Token %s' % (user_token.key)
        )
        assert response.status_code == 201
        json_response = response.json()
        company_key = list(json_response.keys())
        assert self.company_key == company_key.sort()

    def test_company_2(self, user_token, user_company):
        json_data = {
            'name': 'Company private'
        }
        response = self.client.post(
            reverse(
                'company',
                kwargs={'version':1},
            ),
            data=json.dumps(json_data),
            content_type='application/json',
            HTTP_AUTHORIZATION='Token %s' % (user_token.key)
        )
        assert response.status_code == 201
        json_response = response.json()
        company_key = list(json_response.keys())
        assert self.company_key == company_key.sort()
        assert user_token.user.companies.count() == 2

    def test_fetch_company_list(self, user_token, user_company):
        """ """
        response = self.client.get(
            reverse(
                'company',
                kwargs={'version':1}
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Token %s' % (user_token.key)
        )
        assert response.status_code == 200
        json_response = response.json()
        list_key = list(json_response.keys())
        assert self.list_key == list_key.sort()
        for x in json_response['results']:
            company_key = list(x.keys())
            assert self.company_key == company_key.sort()

    def test_search_company(self, user_token, user_company):
        """ """
        for x in range(2, 11):
            CompanyFactory(
                user=user_token.user,
                name='company %s' %(x))
        
        response = self.client.get(
            reverse(
                'company',
                kwargs={'version':1},
            ) + "?" + urllib.parse.urlencode({
                'search':5
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION='Token %s' % (user_token.key)
        )
        assert response.status_code == 200
        json_response = response.json()
        list_key = list(json_response.keys())
        assert self.list_key == list_key.sort()
        assert len(json_response['results']) == 1
        for x in json_response['results']:
            company_key = list(x.keys())
            assert self.company_key == company_key.sort()

    def test_update_company(self, user_token, user_company):
        """ """
        response = self.client.get(
            reverse(
                'company-detail',
                kwargs={
                    'version':1,
                    'company_id':user_company.id
                }
            ),
            content_type='application/json',
            HTTP_AUTHORIZATION='Token %s' %(user_token.key)
        )
        assert response.status_code == 200
        json_response = response.json()
        company_key = list(json_response.keys())
        assert self.company_key == company_key.sort()
