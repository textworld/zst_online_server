from django.shortcuts import render
from schema_info.models import MySQLSchema
from django.http import HttpResponse
from rest_framework import status, viewsets
from schema_info.serializers import MySQLSchemaSerializer, MySQLSchemaNameSerializer, KillMySQLProcessSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filters
import MySQLdb
from django.http import Http404
from .tasks import add, install_mysql_by_ansible
from celery.result import AsyncResult
from zst_project.celery import app
from .serializers import MySQLInstallSerializer

def call_add(request):
    # add(1,2)
    sig = add.si(1,2)
    sig.delay()
    # AsyncResult
    print(result)
    return HttpResponse("success")


def install_mysql(request):
    schema_id = request.POST['schema_id']
    result = install_mysql_by_ansible.delay(schema_id)
    return HttpResponse(result)

def check_mysql_view(request):
    schema_id = request.POST['schema_id']
    mysql_instance = MySQLSchema.objects.get(pk=schema_id)
    install_mysql_by_ansible.delay(mysql_instance)
    return HttpResponse("success")

# 如何根据task result id来查询任务的状态
def query_result(request):
    result = AsyncResult(id="5ce2cd24-4485-4564-9711-0456a055b7c7", app=app)
    print(result.state)
    return HttpResponse(result.state)

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

    @action(detail=False, methods=['post'])
    def install_mysql(self, request, *args, **kwargs):
        serializer = MySQLInstallSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        install_mysql_by_ansible.delay(instance.id)
        return Response("success")

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
        instance = self.get_queryset().get(pk=pk)
        db = self.get_connection(pk)
        c = db.cursor()
        c.execute("show processlist;")
        results = c.fetchall() # 获取所有数据
        columns = ["id", "user", "host", "db", "command", "time", "state", "info"]

        process_lists = []
        for row in results:
            d = {}
            for idx, col_name in enumerate(columns):
                d[col_name] = row[idx]
            process_lists.append(d)
        c.close()
        db.close()
        return Response(process_lists)

    @action(detail=True, methods=['delete'])
    def kill_process_list(self, request, pk=None, *args, **kwargs):
        if pk is None is None:
            raise Http404
        serializer = KillMySQLProcessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        process_id = serializer.validated_data.get('process_id')

        db = self.get_connection(pk)
        c = db.cursor()
        c.execute("kill %d" % process_id)
        c.close()
        db.close()
        return Response("success")

    def get_connection(self, schema_id):
        instance = self.get_queryset().get(pk=schema_id)
        db = MySQLdb.connect(host=instance.host_ip, port=instance.port, user="root",
                passwd="afTD]$]yQ@2:{LQSEQ6bt$]F1mK}Kt#1", db=instance.schema, connect_timeout=2)
        return db
