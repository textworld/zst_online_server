from rest_framework import serializers
from .models import SchemaModel, InstanceModel, AnsibleTaskResult
from rest_framework.exceptions import ValidationError


class InstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstanceModel
        fields = '__all__'


class SchemaSerializer(serializers.ModelSerializer):
    instances = InstanceSerializer(many=True, read_only=True)

    class Meta:
        model = SchemaModel
        fields = '__all__'


class KillMySQLProcessSerializer(serializers.Serializer):
    process_id = serializers.IntegerField(min_value=1)


class MySQLInstallSerializer(serializers.Serializer):
    host_ip = serializers.CharField(max_length=64)
    port = serializers.IntegerField()
    schema = serializers.CharField(max_length=64)

    def validate(self, attrs):
        if InstanceModel.objects.filter(host_ip=attrs['host_ip'],
                                        port=attrs['port']).exists():
            raise ValidationError('this instance has already exist')

        if not SchemaModel.objects.filter(name=attrs['schema']).exists():
            raise ValidationError('schema is not exist')

        return attrs

    def create(self, validated_data):
        schema = SchemaModel.objects.get(name=validated_data['schema'])

        instance = InstanceModel.objects.create(host_ip=validated_data['host_ip'],
                                                port=validated_data['port'], schema=schema,
                                                status=InstanceModel.PENDING, role="master")
        instance.save()
        return instance


class AnsibleTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnsibleTaskResult
        fields = '__all__'