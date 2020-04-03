from django.shortcuts import render

# Create your views here.
import logging
from platreport.platreport_serializer.platreport_serializer import DailyReportModel, DailyReportListSerializers
from rest_framework.generics import ListAPIView, RetrieveAPIView
from common.keda_baseclass import KedaWarningBaseAPIView

logger = logging.getLogger('ops.' + __name__)


class DailyReport(KedaWarningBaseAPIView, ListAPIView):
    serializer_class = DailyReportListSerializers

    def get_queryset(self):
        return DailyReportModel.objects.filter(date=self.kwargs.get('date'))


class DailyReportDetail(KedaWarningBaseAPIView, RetrieveAPIView):
    lookup_field = 'report_type'
    serializer_class = DailyReportListSerializers

    def get_queryset(self):
        return DailyReportModel.objects.filter(date=self.kwargs.get('date'))
