from rest_framework import serializers
from .models import Host
from schema_info.models import *

class HostSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=30)
    memory = serializers.CharField(max_length=30)
    cpu = serializers.CharField(max_length=30)

    def create(self, validated_data):
        h = Host(**validated_data)
        h.save()
        return h

    def update(self, instance, validated_data):
        validated_data.pop('name')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class MySQLSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MySQLSchema
        fields = '__all__'


class MySQLSchemaNameSerializer(serializers.Serializer):
    schema = serializers.CharField(max_length=64, required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class KillMySQLProcessSerializer(serializers.Serializer):
    process_id = serializers.IntegerField(min_value=1)



