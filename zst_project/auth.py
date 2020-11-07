from rest_framework.authentication import SessionAuthentication, BasicAuthentication
# 安全的HTTP请求 GET HEAD OPTION
# 非安全 POST PUT
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening