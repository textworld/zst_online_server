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


class MySQLInstallSerializer(serializers.Serializer):
    host_ip = serializers.CharField(max_length=64)
    port = serializers.IntegerField()
    schema = serializers.CharField(max_length=64)

    def create(self, validated_data):
        print(validated_data)
        schema = MySQLSchema(host_ip=validated_data['host_ip'],
                             port=validated_data['port'], schema=validated_data['schema'],
                             status=MySQLSchema.PENDING, role="master")
        schema.save()
        return schema


class MySQLSchemaNameSerializer(serializers.Serializer):
    schema = serializers.CharField(max_length=64, required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class MySQLInstallSerializer(serializers.Serializer):
    host_ip = serializers.CharField(max_length=64)
    port = serializers.IntegerField()
    schema = serializers.CharField(max_length=64)

    def create(self, validated_data):
        print(validated_data)
        schema = MySQLSchema(host_ip=validated_data['host_ip'],
                             port=validated_data['port'], schema=validated_data['schema'],
                             status=MySQLSchema.PENDING, role="master")
        schema.save()
        return schema


class KillMySQLProcessSerializer(serializers.Serializer):
    process_id = serializers.IntegerField(min_value=1)


class AnsibleTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnsibleTaskResult
        fields = '__all__'