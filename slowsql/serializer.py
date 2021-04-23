from slowsql.models import AlarmSettingModel
from rest_framework import serializers
from schema_info.models import MySQLSchema


class AlarmSettingSerializer(serializers.ModelSerializer):
    # schema_name = serializers.CharField(required=True, write_only=True)
    #schema_name = serializers.SlugRelatedField(many=False, read_only=True, slug_field='schema')
    schema = serializers.SlugRelatedField(many=False, slug_field='schema', queryset=MySQLSchema.objects.all(), allow_null=False)

    class Meta:
        model = AlarmSettingModel
        fields = '__all__'

    # def validate_schema(self, value):
    #     if not MySQLSchema.objects.filter(schema=value).exists():
    #         raise serializers.ValidationError("schema {} is not exist".format(value))
    #     return value

    # def create(self, validated_data):
    #     schema = MySQLSchema.objects.filter(schema=validated_data['schema_name']).first()
    #     validated_data['schema'] = schema
    #     del validated_data['schema_name']
    #     return AlarmSettingModel.objects.create(**validated_data)

class SchemaAlarmSerializer(serializers.Serializer):
    query_time = serializers.IntegerField(min_value=0, required=True)
    query_count = serializers.IntegerField(min_value=0, required=True)
    schema = serializers.SlugRelatedField(many=False, slug_field='schema', queryset=MySQLSchema.objects.all(), allow_null=False)


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

