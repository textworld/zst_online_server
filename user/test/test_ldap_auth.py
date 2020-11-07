from django.test import TestCase
from user.ldap_backend import LdapBackend
from django.test.utils import override_settings

class LdapAuthTestCase(TestCase):
    def setUp(self):
        pass

    @override_settings(BIND_DN='uid=admin,ou=system', BIND_PASSWORD='secret')
    def test_auth_test(self):
        """Animals that can speak are correctly identified"""
        backend = LdapBackend()
        backend.authenticate(None, username="apple", password="ffffff")
