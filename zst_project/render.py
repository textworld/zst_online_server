from rest_framework.renderers import BaseRenderer
from rest_framework.utils import json
from rest_framework.views import exception_handler
from rest_framework.response import Response
import logging


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
                response_dict['code'] = response.status_code
                response_dict['message'] = data

        data = response_dict
        return json.dumps(data)


def my_api_exception_handler(exec, context):
    logging.exception("exception occur: %s", exec)
    response = exception_handler(exec, context)
    if response is None:
        response = Response("internal error", status_cdoe=5000)

    return response
