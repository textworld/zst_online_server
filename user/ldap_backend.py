import ldap
from django.conf import settings
from django.contrib.auth import get_user_model


class LdapBackend:
    _connection_bound = False
    _connection = None

    def authenticate(self, request, username=None, password=None, **kwargs):
        results = self.connection.search_s('o=zst_python,dc=example,dc=com', ldap.SCOPE_SUBTREE, "(uid=%s)" % username)
        if results is not None and len(results) == 1:
            u = results[0]
            print(u)
            user_dn = u[0]
            try:
                self._bind_as(user_dn, password, True)
                query_field = "username"
                UserModel = get_user_model()

                try:
                    user = UserModel.objects.get(username=username)
                except UserModel.DoesNotExist:
                    user = UserModel(username=username)
                    built = True
                else:
                    built = False

                if built:
                    user.set_unusable_password()
                    user.save()
                return user
            except ldap.INVALID_CREDENTIALS:
                return None

    def _get_connection(self):
        if self._connection is None:
            self._connection = ldap.initialize('ldap://127.0.0.1:10389', bytes_mode=False)
            # option和tls
        return self._connection

    def _bind(self):
        #self._bind_as(self.settings.BIND_DN, self.settings.BIND_PASSWORD, sticky=True)
        self._bind_as(settings.ZST_LDAP_BIND_DN_STR, settings.ZST_LDAP_BIND_DN_PASSWORD, sticky=True)

    def _bind_as(self, bind_dn, bind_password, sticky=False):
        self._get_connection().simple_bind_s(bind_dn, bind_password)
        self._connection_bound = sticky

    @property
    def connection(self):
        if not self._connection_bound:
            self._bind()

        return self._get_connection()

