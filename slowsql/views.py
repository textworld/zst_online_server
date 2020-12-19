from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from elasticsearch_dsl import Q
from rest_framework import viewsets
from rest_framework.response import Response

from slowsql.esmodel import SlowQuery
# class BaseFilter:
#     def __init__(self, search):
#         return []
#
#     def query(self,search):
#         return []
# class BaseField:
#     query_name = "match"
#     def __init__(self, field_name=None, must=True, in_filter=False, *args, **kwargs):
#         pass
#
#     def query(self, must_ctx, must_not_ctx, should_ctx, filter_ctx):
#         if self.must is True:
#             must_ctx.append(Q(self.query_name, ))
#
# class KeywordField(BaseField):
#     pass
#
# class MyFilter(BaseFilter):
#     schema = KeywordField(field_name="schema")


class UserViewSet(viewsets.ViewSet):
    def get_int_params(self, request, name, default):
        val = request.query_params.get(name)
        if isinstance(val, str) and val.isnumeric():
            val = int(val)
        else:
            val = default
        return val


    def list(self, request):
        start = request.query_params.get('start', None)
        end = request.query_params.get('end', None)
        schema = request.query_params.get('schema', None)
        page_num = self.get_int_params(request, 'page_num', 1)
        page_size = self.get_int_params(request, 'page_size', 1)

        s = SlowQuery.search()
        print((page_num-1)*page_size)
        print((page_num*page_size))
        s = s[(page_num-1)*page_size:(page_num*page_size)]
        s = s.sort('-@timestamp')
        options = {
            'gte': start,
            'lte': end
        }
        must = []
        if schema is not None:
            must.append(Q('terms', schema__keyword=schema))
        q = Q('bool',
              must=must,
              filter=[Q('range', **{'@timestamp': options})])
        result = s.query(q).execute()
        results = []
        for r in result:
            results.append(r.to_dict())
        print(len(results))
        return Response(results)

