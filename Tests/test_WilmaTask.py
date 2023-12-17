import os
import unittest
import requests

from WilmaTask import wilma_signin

#Testaa Wilman kirjautumista
class TestWilmaSignIn(unittest.TestCase):

    def test_valid_login(self):
        login_req, session = wilma_signin()
        self.assertEqual(login_req.status_code, 200)
        self.assertIsInstance(session, requests.Session)
