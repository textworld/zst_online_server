from rest_framework import serializers
from .models import SchemaModel, InstanceModel, AnsibleTaskResult, AlarmSettingModel
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

# 全局告警设置序列化器
class AddGlbAlarmSerializer(serializers.Serializer):
    query_time = serializers.IntegerField(min_value=0, required=True)
    query_count = serializers.IntegerField(min_value=0, required=True)

    def validate(self, attrs):
        if attrs['query_time'] is None and attrs['query_count'] is None:
            raise serializers.ValidationError("query_time，query_count不能全为空")
        return attrs

    def create(self, validated_data):
        settings = AlarmSettingModel.objects.filter(schema=None).order_by('-id')
        if settings.exists():
            first = settings.first()
            first.query_time = validated_data.get('query_time', first.query_time)
            first.query_count = validated_data.get('query_count', first.query_count)
            first.save()
            return first
        else:
            s = AlarmSettingModel()
            s.schema = None
            s.query_count = validated_data['query_count']
            s.query_time  = validated_data['query_time']
            s.save()
            return s


class AlarmSettingSerializer(serializers.ModelSerializer):
    #schema = serializers.SlugRelatedField(many=False, slug_field='schema', queryset=MySQLInstance.objects.all(), allow_null=False)

    class Meta:
        model = AlarmSettingModel
        fields = '__all__'

    def validate(self, data):
        if not data['type']:
            raise serializers.ValidationError("setting type is required")

        return data

    # def validate_schema(self, value):
    #     Model = self.Meta.model
    #     row = Model.objects.filter(schema=value).exists()
    #     if row:
    #         raise serializers.ValidationError("the setting of schema {} has exist".format(value))
    #     return value

    def create(self, validated_data):
        print(validated_data["schema"])
        Model = self.Meta.model
        if Model.objects.exclude(delete=True).filter(schema=validated_data["schema"]).exists():
            raise serializers.ValidationError("the setting of schema {} has exist".format(validated_data["schema"]))
        return AlarmSettingModel.objects.create(**validated_data)


class SchemaAlarmSerializer(serializers.Serializer):
    query_time = serializers.IntegerField(min_value=0, required=True)
    query_count = serializers.IntegerField(min_value=0, required=True)
    #schema = serializers.SlugRelatedField(many=False, slug_field='schema', queryset=MySQLInstance.objects.all(), allow_null=False)
    schema = serializers.CharField()
