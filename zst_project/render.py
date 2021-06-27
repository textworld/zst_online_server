from rest_framework.renderers import BaseRenderer
from rest_framework.utils import json
from rest_framework.views import exception_handler
from rest_framework.response import Response
import logging
from rest_framework import exceptions, status

class ApiRenderer(BaseRenderer):
    media_type = 'application/json'
    format = 'json'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_dict = {
            'code': 2000,
            'data': {},
            'message': '',
        }
        if renderer_context is not None:
            response = renderer_context['response']
            if response.status_code == 200:
                response_dict['data'] = data
            else:
                response_dict['code'] = int(int(response.status_code / 100) * 1000 + response.status_code % 100)
                response_dict['message'] = data
                response.status_code = 200

        data = response_dict
        return json.dumps(data)


def my_api_exception_handler(exc, context):
    logging.exception("exception occur: %s", exc)
    if isinstance(exc, exceptions.ValidationError):
        message = ""
        if isinstance(exc.detail, list):
            message = exc.detail[0]
        response = Response(message, status=exc.status_code)
    else:
        response = exception_handler(exc, context)
    if response is None:
        response = Response("internal error", status=500)

    return response
