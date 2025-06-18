from cfenv import AppEnv
from sap import xssec

class Authorization:
    def __init__(self, request):
        self._env = AppEnv()
        self._uaa_service = self._env.get_service(name='adt-mcp-server-pyuaa').credentials
        self._request = request
        self._security_context = None

    def get_access_token(self):
        access_token = self._request.headers.get('authorization')[7:]
        return access_token

    def get_security_context(self):
        access_token = self.get_access_token()

        if not self._security_context:
            try:
                self._security_context = xssec.create_security_context(access_token, self._uaa_service)
            except RuntimeError:
                return None

        return self._security_context

    def is_authorized(self):
        if 'authorization' not in self._request.headers:
            return False

        access_token = self.get_access_token()
        
        security_context = self.get_security_context()

        if not security_context:
            return False

        isAuthorized = security_context.check_scope('uaa.resource')
        return isAuthorized
    
