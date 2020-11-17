from django.urls import path, include
from .views import bill_data, FileUploadView, BillRecordView, category_update

urlpatterns = [
    path('bill_data/', bill_data),
    path('bill_data/import/csv/', FileUploadView.as_view()),
    path('bill_record/', BillRecordView.as_view()),
    path('category/update/<int:cate_id>/', category_update)
]