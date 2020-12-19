from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from elasticsearch_dsl import Q, A
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from slowsql.esmodel import SlowQuery
aggs = {
    "aggs": {
        "date": {
            "date_histogram": {
                "field": "@timestamp",
                "interval": "hour"
            },
            "aggs": {
                "scham": {
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
        paginator = PageNumberPagination()

        if is_aggr_by_hash:
            aggs = {
                "aggs": {
                    "date": {
                        "date_histogram": {
                            "field": "@timestamp",
                            "interval": "hour"
                        },
                        "aggs": {
                            "scham": {
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

            # timeAggs = A('date_histogram')
            # schemaAggs = A('terms', field='schema.keyword')
            # fingerAggs = A('terms', field='hash.keyword')
            # rowsExaminedAvg = A('avg', field=' ')
            # queryTimeAvg = A('avg', field='query_time')
            # s.aggs.bucket('date', timeAggs).bucket('hash', fingerAggs).metric('rowsExaminedAvg',
            #                                                                   rowsExaminedAvg).metric('queryTimeAvg',
            #                                                                                           queryTimeAvg)
            result = s.execute().aggregations
            print(result)

            results = []
            for date_bucket in result['date']['buckets']:
                for hash_bucket in date_bucket['hash']['buckets']:
                    print(hash_bucket)
                    # results.append({
                    #     '@timestamp': date_bucket['key_as_string'],
                    #     ''
                    # })

        data = paginator.paginate_queryset(s, request)
        data = [q.to_dict() for q in data]
        return paginator.get_paginated_response(data)
