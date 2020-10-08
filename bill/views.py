from django.shortcuts import render
from django.http import JsonResponse
from .models import BillRecord, Category
from .serializers import BillRecordSerializer
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
import csv
import datetime
import codecs
from django.http import Http404
from dateutil.relativedelta import relativedelta
# Create your views here.

# 返回账单数据
def bill_data(request):
    data = {
        'data': []
    }
    records = BillRecord.objects.all()
    data['data'] = BillRecordSerializer(records, many=True).data
    return JsonResponse(data)


def category_update(request, cate_id):
    if request.method == 'POST':
        Category.update_path(cate_id)
        return JsonResponse({"code": 0})

    raise Http404

class BillRecordView(APIView):
    def delete(self, request):
        year = request.GET['year']
        month = request.GET['month']
        start_date = "{}-{}-01".format(year, month)
        dt_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = (dt_obj + relativedelta(months=+1)).date()
        BillRecord.objects.filter(date__gte=dt_obj.date(), date__lt=end_date).delete()
        return Response(status=200)


class FileUploadView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, format=None):
        file_obj = request.data["file"]
        f_csv = csv.reader(codecs.iterdecode(file_obj, 'utf-8'))
        headers = next(f_csv)
        for row in f_csv:
            category_label = row[3]
            if category_label and not Category.objects.filter(label=category_label).exists():
                print("add category {}".format(category_label))
                Category.create_cate(category_label, 0).save()
            r = self.parse_csv_row(row)
            r.save()
        return Response(status=201)

    def parse_csv_row(self, row):
        name = row[1]
        price = float(row[2])
        date = row[0].replace("/", "-")
        category_id = None
        if row[3] and Category.objects.filter(label=row[3]).exists():
           category_id = Category.objects.get(label=row[3])
        return BillRecord(name=name, price=price, date=date, category_id=category_id)