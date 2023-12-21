# vendors/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Vendor
from .serializers import VendorSerializer
from purchase_orders.models import PurchaseOrder
from datetime import timedelta
from django.db import models

class VendorListCreateView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    
class VendorRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    

class VendorPerformanceView(generics.RetrieveAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        performance_metrics = self.calculate_performance_metrics(instance)
        serializer.data.update(performance_metrics)
        return Response(serializer.data)

    def calculate_performance_metrics(self, vendor):
        completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
        total_pos = completed_pos.count()

        on_time_delivery_rate = completed_pos.filter(delivery_date__lte=models.F('acknowledgment_date')).count() / total_pos if total_pos > 0 else 0
        quality_rating_avg = completed_pos.aggregate(models.Avg('quality_rating'))['quality_rating__avg'] or 0
        response_times = completed_pos.exclude(acknowledgment_date=None).annotate(
            response_time=models.ExpressionWrapper(
                models.F('acknowledgment_date') - models.F('issue_date'),
                output_field=models.DurationField()
            )
        ).aggregate(models.Avg('response_time'))['response_time__avg'] or 0
        fulfillment_rate = completed_pos.filter(acknowledgment_date__isnull=False).count() / total_pos if total_pos > 0 else 0

        return {
            'on_time_delivery_rate': on_time_delivery_rate,
            'quality_rating_avg': quality_rating_avg,
            'average_response_time': response_times.total_seconds() / 60,  # Convert to minutes
            'fulfillment_rate': fulfillment_rate
        }
