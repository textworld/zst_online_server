from rest_framework import serializers


class BillRecordSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    price = serializers.DecimalField(max_digits=8, decimal_places=2, coerce_to_string=False, localize=False)
    category_path = serializers.SlugRelatedField(source='category_id', read_only=True, slug_field='path')
    date = serializers.DateField()
