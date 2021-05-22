from rest_framework import serializers
from siteapp.models import NewsModel, HistoryOpModel


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsModel
        fields = '__all__'

class HistoryOpSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryOpModel
        fields = '__all__'
