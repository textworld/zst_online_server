import MySQLdb
from django.http import Http404
from django.http import HttpResponse
from rest_framework import filters, exceptions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from zst_project.common import CustomPagination
from .es_document import SlowQuery
from .es_helper import get_aggs, get_results
from .serializers import *
from .tasks import add
from .tasks import install_mysql_by_ansible
from .models import AlarmSettingModel
from .serializers import SchemaAlarmSerializer


def add_request(request):
    result = add.delay(3, 3)
    print(result)
    return HttpResponse("success")


class SchemaViewSet(viewsets.ModelViewSet):
    queryset = SchemaModel.objects.all()
    serializer_class = SchemaSerializer

    pagination_class = CustomPagination

    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @action(detail=False, methods=['get'])
    def get_distinct_schema_names(self, request, *args, **kwargs):
        queryset = self.get_queryset().values('name').distinct()
        # 我们这里没有使用序列化器，而是将query set变成了一个列表返回
        name_list = [d["name"] for d in list(queryset)]
        return Response(name_list)


class InstanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InstanceModel.objects.all()
    serializer_class = InstanceSerializer
    pagination_class = CustomPagination

    def filter_queryset(self, queryset):
        schema = self.request.query_params.get('schema', None)
        if schema:
            queryset = queryset.filter(schema=schema)
        return queryset

    @action(detail=False, methods=['POST'])
    def install_mysql(self, request, *args, **kwargs):
        serializer = MySQLInstallSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        install_mysql_by_ansible.delay(instance.id)

        return Response("success")

    @action(detail=True, methods=['GET'])
    def get_process_list(self, request, pk=None, *args, **kwargs):
        if pk is None:
            raise Http404
        try:
            db = self.get_connection(pk)
            c = db.cursor()
            c.execute("show processlist;")
            results = c.fetchall()  # 获取所有数据
            columns = ["id", "user", "host", "db", "command", "time", "state", "info"]

            process_list = []
            for row in results:
                d = {}
                for idx, col_name in enumerate(columns):
                    d[col_name] = row[idx]
                process_list.append(d)
            c.close()
            db.close()
            return Response(process_list)
        except Exception:
            raise APIException("无法获取process list")

    @action(detail=True, methods=['delete'])
    def kill_process_list(self, request, pk=None):
        if pk is None:
            raise Http404
        serializer = KillMySQLProcessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        process_id = serializer.validated_data.get('process_id')
        db = self.get_connection(pk)
        c = db.cursor()
        c.execute("kill %d;" % process_id)
        c.close()
        db.close()
        return Response("success")

    def get_connection(self, instance_id):
        instance = self.get_queryset().get(pk=instance_id)
        # TODO: dbUtils 连接池性能更好
        db = MySQLdb.connect(host=instance.host_ip, port=instance.port, user="root",
                             passwd="dI4,,%2zYPqqQ[w/:m(ZiuK(wUeg^mW(", db=instance.schema.name, connect_timeout=2)
        return db


class AnsibleResultViews(viewsets.ReadOnlyModelViewSet):
    queryset = AnsibleTaskResult.objects.all()
    serializer_class = AnsibleTaskSerializer
    pagination_class = CustomPagination
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('start_time',)


class SlowSQLViewSet(viewsets.ViewSet):
    @action(methods=['get'], detail=False)
    def search(self, request, *args, **kwargs):
        s = self.get_query_by_params(request)
        interval = request.query_params.get('interval', '1d')

        is_aggr_by_hash = request.query_params.get('is_aggr_by_hash', False)
        if isinstance(is_aggr_by_hash, str) and is_aggr_by_hash.lower() == 'true':
            is_aggr_by_hash = True
        else:
            is_aggr_by_hash = False
        aggs = self.get_aggs_by_sql_id(interval)
        if is_aggr_by_hash:
            get_aggs(s.aggs, aggs)
            result = s.execute().aggregations
            rs = get_results(aggs, result)

        paginator = CustomPagination()
        if is_aggr_by_hash:
            data = paginator.paginate_queryset(rs, request)
        else:
            data = paginator.paginate_queryset(s, request)
            data = [q.to_dict() for q in data]

        return paginator.get_paginated_response(data)

    def get_aggs_by_sql_id(self, interval):
        return {
                "aggs": {
                    "date": {
                        "date_histogram": {
                            "field": "@timestamp",
                            "calendar_interval": interval
                        },
                        "aggs": {
                            "schema": {
                                "terms": {
                                    "field": "schema.keyword"
                                },
                                "aggs": {
                                    "sql_id": {
                                        "terms": {
                                            "field": "sql_id.keyword"
                                        },
                                        "aggs": {
                                            "rows_sent": {
                                                "avg": {
                                                    "field": "rows_sent"
                                                }
                                            },
                                            "rows_examined": {
                                                "avg": {
                                                    "field": "rows_examined"
                                                }
                                            },
                                            "query_time_sec": {
                                                "avg": {
                                                    "field": "query_time_sec"
                                                }
                                            },
                                            "sql": {
                                                "top_hits": {
                                                    "_source": [
                                                        "finger",
                                                        "@timestamp"
                                                    ],
                                                    "sort": [
                                                        {
                                                            "@timestamp": {
                                                                "order": "desc"
                                                            }
                                                        }
                                                    ],
                                                    "size": 1
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
    # 通用获取参数
    def get_query_by_params(self, request, sorts=None):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        s = SlowQuery.search()
        if start is None or not isinstance(start, str) or len(start.strip()) == 0:
            start = None
        if end is None or not isinstance(end, str) or len(end.strip()) == 0:
            end = None

        if start is not None and end is not None:
            options = {
                # greater or equal than  -> gte 大于等于
                # greater than  -> gt 大于
                # little or equal thant -> lte 小于或等于
                'gte': start,
                'lte': end
            }
            s = s.filter('range', **{'@timestamp': options})

        sorts = request.query_params.get('sorts', sorts)
        if isinstance(sorts, str) and len(sorts) > 0:
            sorts = [item.strip() for item in sorts.split(",") if len(item.strip()) > 0]
            s = s.sort(*sorts)
        else:
            s = s.sort('-@timestamp')

        schema = request.query_params.get('schema', None)
        if schema is not None and len(schema) > 0:
            s = s.filter('term', schema__keyword=schema)

        keyword = request.query_params.get('keyword', None)
        if keyword is not None and len(keyword) > 0:
            s = s.query('match', slowsql=keyword)

        sql_id = request.query_params.get('sql_id', None)
        if sql_id is not None and len(sql_id) > 0:
            s = s.filter('term', sql_id__keyword=sql_id)


        return s


class AlarmSettingViewSet(viewsets.ModelViewSet):
    queryset = AlarmSettingModel.objects.exclude(schema__isnull=True).exclude(delete=True)
    serializer_class = AlarmSettingSerializer

    @action(detail=False, methods=['post', 'get'])
    def global_setting(self, request, *args, **kwargs):
        if request.method == 'POST':
            s = AddGlbAlarmSerializer(data=request.data)
            s.is_valid(raise_exception=True)
            instance = s.save()
            return Response("success")

        settings = AlarmSettingModel.objects.filter(schema=None).order_by("-id")
        if not settings.exists():
            raise exceptions.NotFound('global setting was not found')

        return Response(AddGlbAlarmSerializer(settings.first()).data)

    @action(detail=False, methods=['post', 'get'])
    def schema_settings(self, request, *args, **kwargs):
        if request.method == 'POST':
            # 保存设置
            return Response([])
        settings = AlarmSettingModel.objects.filter(type__exact=AlarmSettingModel.Type.Schema, delete=False).all()
        if settings.count() == 0:
            return Response([])
        return Response(SchemaAlarmSerializer(settings, many=True).data)