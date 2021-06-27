from rest_framework import serializers
from .models import SchemaModel


class InstanceSerializer(serializers.Serializer):
    ip = serializers.CharField(required=True, allow_blank=False, min_length=6, max_length=30)
    port = serializers.IntegerField(required=True)
    schema = serializers.CharField(required=True)


class SchemaSerializer(serializers.Serializer):
    instances = InstanceSerializer(many=True, read_only=True)

    class Meta:
        model = SchemaModel
        fields = ['name', 'instances', 'create_time']
