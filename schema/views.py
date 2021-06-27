from rest_framework import viewsets
from rest_framework.response import Response

from .models import *
from .serializers import *


class SchemaViewSet(viewsets.ModelViewSet):
    queryset = SchemaModel.objects.all()
    serializer_class = SchemaSerializer
