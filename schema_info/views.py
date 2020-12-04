from django.shortcuts import render
from schema_info.models import MySQLSchema
from rest_framework import status, viewsets
from schema_info.serializers import MySQLSchemaSerializer, MySQLSchemaNameSerializer, KillMySQLProcessSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filters
import MySQLdb
from django.http import Http404
from django.http import HttpResponse
from schema_info.tasks import add, send_mail, check_mysql_group, check_mysql
from zst_project.celery import app
from celery.result import AsyncResult
from celery import Task, chain, group


def group_request(request):
    fn = group(check_mysql.s(i) for i in range(10))
    group_result = fn.delay()
    print(group_request)
    return HttpResponse("success")


def add_request(request):
    result = send_mail.delay("text.zwb@outlook.com", "123")
    print(result)
    return HttpResponse("success")

def query_task_result(request):
    result = AsyncResult(id='57409e6a-d11a-47dc-9bac-7d29bb66d8e1', app=app)
    print(result.state)
    return HttpResponse("success")

def login_test(request):
    return HttpResponse({
        'code': 40400
    })


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page_num'
    max_page_size = 500


class SchemaViewSet(viewsets.ModelViewSet):
    queryset = MySQLSchema.objects.all()
    serializer_class = MySQLSchemaSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['status', 'schema', 'host_ip', 'port']

    @action(detail=False, methods=['get'])
    def get_distinct_schema_names(self, request, *args, **kwargs):
        queryset = self.get_queryset().values('schema').distinct()
        # 我们这里没有使用序列化器，而是将query set变成了一个列表返回
        name_list = [d["schema"] for d in list(queryset)]
        return Response(name_list)

    @action(detail=True, methods=['get'])
    def get_process_list(self, request, pk=None, *args, **kwargs):
        if pk is None:
            raise Http404

        db = self.get_connection(pk)
        c = db.cursor()
        c.execute('show processlist;')
        results = c.fetchall()
        columns = ["id", 'user', 'host', 'db', 'command', 'time', 'state', 'info']

        process_list = []
        for row in results:
            d = {}
            for idx, col_name in enumerate(columns):
                d[col_name] =row[idx]
            process_list.append(d)
        c.close()
        db.close()
        return Response(process_list)

    @action(detail=True, methods=['delete'])
    def kill_process_list(self, request, pk=None):
        if pk is None:
            raise Http404
        serializer = KillMySQLProcessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        process_id = serializer.validated_data.get('process_id')
        db = self.get_connection(pk)
        c = db.cursor()
        print("kill %d;" % process_id)
        c.execute("kill %d;" % process_id)
        c.close()
        db.close()
        return Response("success")


    def get_connection(self, pk):
        instance = self.get_queryset().get(pk=pk)
        return MySQLdb.connect(host=instance.host_ip, port=instance.port, user='root',
                             passwd='afTD]$]yQ@2:{LQSEQ6bt$]F1mK}Kt#1', db=instance.schema)
