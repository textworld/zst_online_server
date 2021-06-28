import ldap
from django.conf import settings
from django.contrib.auth import get_user_model


class LdapBackend:
    _connection_bound = False
    _connection = None

    def get_user(self, user_id):
        user = None

        try:
            user = get_user_model().objects.get(pk=user_id)
        except get_user_model().ObjectDoesNotExist:
            pass

        return user

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            results = self.connection.search_s(settings.ZST_LDAP_SETTING.get('search_ou'), ldap.SCOPE_SUBTREE,
                                            settings.ZST_LDAP_SETTING.get('search_filter') % username)
            if results is not None and len(results) == 1:
                u = results[0]
                user_dn = u[0]

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
            self._connection = ldap.initialize('ldap://' + settings.ZST_LDAP_SETTING.get('url'), bytes_mode=False)
            # option和tls
        return self._connection

    def _bind(self):
        #self._bind_as(self.settings.BIND_DN, self.settings.BIND_PASSWORD, sticky=True)
        self._bind_as(settings.ZST_LDAP_SETTING.get('bind_dn'), settings.ZST_LDAP_SETTING.get('bind_password'), sticky=True)

    def _bind_as(self, bind_dn, bind_password, sticky=False):
        self._get_connection().simple_bind_s(bind_dn, bind_password)
        self._connection_bound = sticky

    @property
    def connection(self):
        if not self._connection_bound:
            self._bind()

        return self._get_connection()

