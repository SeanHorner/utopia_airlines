import requests
import json
import unittest


class ApiTests(unittest.TestCase):

    USERS_API = "http://users:5000/api"

    # ------------------------------------------------
    #                   Create Tests
    # ------------------------------------------------

    def create_response_probe(self, url, payload):
        headers = {'Content-Type': 'application/json'}

        # convert dict to json string by json.dumps() for body data.
        resp = requests.post(url, headers=headers, data=json.dumps(payload))

        # Validate response headers and body contents, e.g. status code.
        self.assertEqual(resp.status_code, 200, "Bad status code")
        resp_body = resp.json()
        self.assertEqual(resp_body['url'], url, "Bad return URL")

        # print response full body as text
        print(resp.text)

        return resp_body

    def test_user_role_post(self):
        url = 'http://users:5000/api/user_role/create'

        # Body
        payload = {
            'iata_id': 'ZZZ',
            'city': 'Zamzabeea, ZZ',
            'name': 'Zamzara Internaional',
            'longitude': 0.00,
            'latitude': 0.00,
            'elevation': 0
        }

        resp_json = ApiTests.create_response_probe(self, url=url, payload=payload)

        print(resp_json)

    def test_user_post(self):
        url = 'http://users:5000/api/user_role/create'

        # Body
        payload = {
            'iata_id': 'ZZZ',
            'city': 'Zamzabeea, ZZ',
            'name': 'Zamzara Internaional',
            'longitude': 0.00,
            'latitude': 0.00,
            'elevation': 0
        }

        resp_json = ApiTests.create_response_probe(self, url=url, payload=payload)

        print(resp_json)

    # ------------------------------------------------
    #                   Retrieval Tests
    # ------------------------------------------------

    # ------------------------------------------------
    #                   Update Tests
    # ------------------------------------------------

    # ------------------------------------------------
    #                   Delete Tests
    # ------------------------------------------------


if __name__ == "__main__":
    unittest.main()
