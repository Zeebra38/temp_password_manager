import json
import unittest

import application


class RESTAPITests(unittest.TestCase):
    base_url = '/pwd.mng/api/v1.0'

    def setUp(self):
        app = application.create_app(True)
        app.config.update(TESTING=True)
        self.test_client = app.test_client()  # создание клиента

        # регистрация нового пользователя
        response = self.test_client.post(f'{self.base_url}/register',
                                         data=json.dumps({'username': 'test_user'}),
                                         content_type='application/json')
        self.token = response.json['token']
        self.tokens_to_delete = []

        # добавление записей в БД
        self.test_client.post(f'{self.base_url}/logins',
                              query_string={'token': self.token},
                              json={'login': 'test_main_login1', 'password': 'test_main_password1'})
        self.test_client.post(f'{self.base_url}/logins',
                              query_string={'token': self.token, 'generate': 1})

    def tearDown(self):
        self.test_client.delete(f'{self.base_url}/delete_user', query_string={'token': self.token})
        for token in self.tokens_to_delete:
            self.test_client.delete(f'{self.base_url}/delete_user', query_string={'token': token})

    def test_register(self):
        response = self.test_client.post(f'{self.base_url}/register',
                                         data=json.dumps({'username': 'test_register'}),
                                         content_type='application/json')
        self.assertTrue(response.status_code == 201)
        self.assertTrue(response.json)
        self.assertTrue('status' in response.json)
        self.assertTrue('token' in response.json)
        self.tokens_to_delete.append(response.json['token'])

    def test_create_login(self):
        login1 = 'test_create_login1'
        password1 = 'test_create_password1'
        login2 = 'test_create_login1'
        password2 = 'test_create_password1'
        site2 = 'test_site2'

        response_without_site = self.test_client.post(f'{self.base_url}/logins',
                                                      query_string={'token': self.token},
                                                      json={'login': login1, 'password': password1})
        self.assertEqual(response_without_site.status_code, 200)
        self.assertTrue(response_without_site.json)
        self.assertEqual(response_without_site.json['status'], 'success')
        self.assertEqual(response_without_site.json['login']['login'], login1)
        self.assertEqual(response_without_site.json['login']['password'], password1)
        self.assertEqual(response_without_site.json['login']['site'], '')

        response_with_site = self.test_client.post(f'{self.base_url}/logins',
                                                   query_string={'token': self.token},
                                                   json={'login': login2, 'password': password2, 'site': site2})
        self.assertEqual(response_with_site.status_code, 200)
        self.assertTrue(response_with_site.json)
        self.assertEqual(response_with_site.json['status'], 'success')
        self.assertEqual(response_with_site.json['login']['login'], login2)
        self.assertEqual(response_with_site.json['login']['password'], password2)
        self.assertEqual(response_with_site.json['login']['site'], site2)

        response_without_token = self.test_client.post(f'{self.base_url}/logins',
                                                       json={'login': login2, 'password': password2, 'site': site2})
        self.assertEqual(response_without_token.status_code, 401)
        self.assertTrue(response_without_token.json)
        self.assertEqual(response_without_token.json['status'], 'error')

        response_without_json = self.test_client.post(f'{self.base_url}/logins',
                                                      query_string={'token': self.token})
        self.assertEqual(response_without_json.status_code, 400)
        self.assertTrue(response_without_json.json)
        self.assertEqual(response_without_json.json['status'], 'error')

    def test_get_logins(self):
        response_all_logins = self.test_client.get(f'{self.base_url}/logins', query_string={'token': self.token})

        self.assertEqual(response_all_logins.status_code, 200)
        self.assertTrue(response_all_logins.json)
        self.assertEqual(response_all_logins.json['status'], 'success')
        self.assertTrue('logins' in response_all_logins.json)
        self.assertEqual(len(response_all_logins.json['logins']), 2)
        self.assertEqual(response_all_logins.json['logins'][0]['login'], 'test_main_login1')
        self.assertEqual(response_all_logins.json['logins'][0]['password'], 'test_main_password1')
        self.assertEqual(response_all_logins.json['logins'][0]['site'], '')

    def test_get_login(self):
        response_one_login = self.test_client.get(f'{self.base_url}/logins/1', query_string={'token': self.token})
        self.assertEqual(response_one_login.status_code, 200)
        self.assertTrue(response_one_login.json)
        self.assertEqual(response_one_login.json['status'], 'success')
        self.assertTrue('login' in response_one_login.json)
        self.assertEqual(response_one_login.json['login']['login'], 'test_main_login1')
        self.assertEqual(response_one_login.json['login']['password'], 'test_main_password1')
        self.assertEqual(response_one_login.json['login']['site'], '')

    def test_patch_login(self):
        new_login = 'updated_login1'
        new_password = 'updated_password1'
        new_site = 'updated_site1'
        response = self.test_client.patch(f'{self.base_url}/logins/1',
                                          query_string={'token': self.token},
                                          json={'login': new_login, 'password': new_password,
                                                'site': new_site})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json)
        self.assertEqual(response.json['status'], 'success')
        self.assertEqual(response.json['login']['login'], new_login)
        self.assertEqual(response.json['login']['password'], new_password)
        self.assertEqual(response.json['login']['site'], new_site)

        response_without_token = self.test_client.post(f'{self.base_url}/logins',
                                                       json={'login': new_login, 'password': new_password,
                                                             'site': new_site})
        self.assertEqual(response_without_token.status_code, 401)
        self.assertTrue(response_without_token.json)
        self.assertEqual(response_without_token.json['status'], 'error')

        response_without_json = self.test_client.post(f'{self.base_url}/logins',
                                                      query_string={'token': self.token})
        self.assertEqual(response_without_json.status_code, 400)
        self.assertTrue(response_without_json.json)
        self.assertEqual(response_without_json.json['status'], 'error')


if __name__ == '__main__':
    unittest.main()
