from slowsql.models import AlarmSettingModel
from rest_framework import serializers
from schema_info.models import MySQLSchema


class AlarmSettingSerializer(serializers.ModelSerializer):
    schema = serializers.SlugRelatedField(many=False, slug_field='schema', queryset=MySQLSchema.objects.all(), allow_null=False)

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

