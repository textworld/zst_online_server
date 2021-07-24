import MySQLdb
from django.http import Http404
from rest_framework import filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import APIException
from zst_project.common import CustomPagination
from .serializers import *
from .models import *
import logging
from .tasks import install_mysql_by_ansible

from django.http import HttpResponse

from .tasks import add

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


