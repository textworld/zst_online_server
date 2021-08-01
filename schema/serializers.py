from rest_framework import serializers
from .models import SchemaModel, InstanceModel, AnsibleTaskResult, AlarmSettingModel
from rest_framework.exceptions import ValidationError
from zst_project.third_parts import soar


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
        settings = AlarmSettingModel.objects.filter(type=AlarmSettingModel.Type.Global).order_by('-id')
        if settings.exists():
            first = settings.first()
            first.query_time = validated_data.get('query_time', first.query_time)
            first.query_count = validated_data.get('query_count', first.query_count)
            first.save()
            return first
        else:
            s = AlarmSettingModel()
            s.schema = None
            s.type = AlarmSettingModel.Type.Global
            s.query_count = validated_data['query_count']
            s.query_time = validated_data['query_time']
            s.save()
            return s


class AlarmSettingSerializer(serializers.ModelSerializer):
    # schema = serializers.SlugRelatedField(many=False, slug_field='schema', queryset=MySQLInstance.objects.all(), allow_null=False)
    sql = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = AlarmSettingModel
        fields = '__all__'

    def validate(self, data):
        if not data['type']:
            raise serializers.ValidationError("setting type is required")

        Model = self.Meta.model

        if data["type"] == Model.Type.SQL and self.context['request'].method == 'post':

            if data["sql"] is None or len(data["sql"].strip()) == 0:
                raise serializers.ValidationError("sql is required")

        return data

    def construct_sql_print(self, validated_data):
        sql_resp = soar.get_sql_id(validated_data['sql'])
        # {'fingerprint': 'select * from a where b = ?', 'id': '4B9BFCF125FF8398', 'sq
        validated_data["sql_print"] = sql_resp["fingerprint"]
        validated_data["sql_id"] = sql_resp["id"]
        validated_data.pop("sql")

    def update(self, instance, validated_data):

        if validated_data.get("query_time"):
            instance.query_time = validated_data["query_time"]
        if validated_data.get("query_count"):
            instance.query_count = validated_data["query_count"]

        if validated_data.get("delete") is not None:
            instance.delete = validated_data["delete"]

        if validated_data.get("stop_alarm"):
            instance.stop_alarm = validated_data["stop_alarm"]

        instance.save()
        return instance

    def create(self, validated_data):
        schema = validated_data["schema"]
        Model = self.Meta.model

        if validated_data["type"] == Model.Type.SQL and validated_data["sql"] is not None:
            sql_resp = soar.get_sql_id(validated_data['sql'])
            # {'fingerprint': 'select * from a where b = ?', 'id': '4B9BFCF125FF8398', 'sq
            validated_data["sql_print"] = sql_resp["fingerprint"]
            validated_data["sql_id"] = sql_resp["id"]
            validated_data.pop("sql")

        if validated_data["type"] == Model.Type.Schema and Model.objects.exclude(delete=True).filter(schema=validated_data["schema"].name,
                                                     type=Model.Type.Schema).exists():
            raise serializers.ValidationError(
                "the setting of schema {} has exist".format(validated_data["schema"].name))

        if validated_data["type"] == Model.Type.SQL and Model.objects.exclude(delete=True) \
                .filter(type=Model.Type.SQL, schema=validated_data["schema"], sql_id=validated_data["sql_id"]).exists():
            raise serializers.ValidationError(
                "the setting of schema {} and sql_id {} has exist".format(schema.name, validated_data["sql_id"]))

        return AlarmSettingModel.objects.create(**validated_data)


class SchemaAlarmSerializer(serializers.Serializer):
    query_time = serializers.IntegerField(min_value=0, required=True)
    query_count = serializers.IntegerField(min_value=0, required=True)
    # schema = serializers.SlugRelatedField(many=False, slug_field='schema', queryset=MySQLInstance.objects.all(), allow_null=False)
    schema = serializers.CharField()
