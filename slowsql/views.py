from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from elasticsearch_dsl import Q, A
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from slowsql.esmodel import SlowQuery


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page_num'
    max_page_size = 500

def build_aggs(agg):
    for k in agg.keys():
        if k != "aggs":
            options = agg.get(k)
            return A(k, **options)


def get_aggs(agg, d):
    if 'aggs' not in d.keys():
        return

    aggs = d.get('aggs')
    if len(aggs.keys()) > 1:
        for metric_name in aggs.keys():
            agg = agg.metric(metric_name, build_aggs(aggs.get(metric_name)))
    elif len(aggs.keys()) == 1:
        k = list(aggs.keys())[0]
        agg = agg.bucket(k, build_aggs(aggs.get(k)))
        get_aggs(agg, aggs.get(k))


def get_results(agg_query, result):
    if 'aggs' not in agg_query.keys():
        return

    aggs = agg_query.get('aggs')
    if len(aggs.keys()) == 1:
        key_name = list(aggs.keys())[0]
        bucket_results = []
        for bucket in result[key_name]['buckets']:
            doc_count = 0
            key_val = ''
            if 'key_as_string' in bucket:
                key_val = bucket.key_as_string
            elif 'key' in bucket:
                key_val = bucket.key
            else:
                raise Exception('no key found in bucket')
            if 'doc_count' in bucket:
                doc_count = bucket.doc_count
            ret = get_results(aggs[key_name], bucket)
            if isinstance(ret, list):
                for r in ret:
                    r[key_name + "_count"] = doc_count
                    r[key_name] = key_val
                bucket_results.extend(ret)
            elif isinstance(ret, dict):
                ret[key_name] = key_val
                bucket_results.append(ret)
        return bucket_results
    else:
        ret = {}
        for key_name in aggs.keys():
            val = result[key_name]['value']
            ret[key_name] = val
        return ret


class SlowSqlViewSet(viewsets.ViewSet):
    def get_int_params(self, request, name, default_val):
        val = request.query_params.get(name, None)

        if val is not None and isinstance(val, str) and val.isnumeric():
            val = int(val)
        else:
            val = default_val
        return val

    def list(self, request, *args, **kwargs):
        # 入参： 开始时间、结束时间、库名、第几页、每页多少个
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        schema = request.query_params.get('schema', None)
        is_aggr_by_hash = request.query_params.get('is_aggr_by_hash', False)
        if isinstance(is_aggr_by_hash, str) and is_aggr_by_hash.lower() == 'true':
            is_aggr_by_hash = True
        else:
            is_aggr_by_hash = False

        interval = request.query_params.get('interval', '10m')

        # 参数验证过程就省略
        s = SlowQuery.search()
        if schema is not None and len(schema) > 0:
            s = s.filter('term', schema__keyword=schema)
        if start is not None and end is not None:
            options = {
                # greater or equal than  -> gte 大于等于
                # greater than  -> gt 大于
                # little or equal thant -> lte 小于或等于
                'gte': start,
                'lte': end
            }
            s = s.filter('range', **{'@timestamp': options})

        s = s.sort('-@timestamp')
        paginator = CustomPagination()

        if is_aggr_by_hash:
            aggs = {
                "aggs": {
                    "date": {
                        "date_histogram": {
                            "field": "@timestamp",
                            "interval": "hour"
                        },
                        "aggs": {
                            "schema": {
                                "terms": {
                                    "field": "schema.keyword"
                                },
                                "aggs": {
                                    "hash": {
                                        "terms": {
                                            "field": "hash.keyword"
                                        },
                                        "aggs": {
                                            "rowsExaminedAvg": {
                                                "avg": {
                                                    "field": "rows_examined"
                                                }
                                            },
                                            "queryTimeAvg": {
                                                "avg": {
                                                    "field": "query_time"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            get_aggs(s.aggs, aggs)

            result = s.execute().aggregations

            rs = get_results(aggs, result)
        if is_aggr_by_hash:
            data = paginator.paginate_queryset(rs, request)
        else:
            data = paginator.paginate_queryset(s, request)
            data = [q.to_dict() for q in data]

        return paginator.get_paginated_response(data)
