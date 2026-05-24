from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Sum, Count
from django.utils import timezone
from decimal import Decimal

from .models import Client, DataSource, EmissionFactor, RawDataUpload, NormalizedEmissionRecord, AuditLog
from .serializers import (ClientSerializer, DataSourceSerializer, 
                          NormalizedEmissionRecordSerializer, AuditLogSerializer)
from .parsers import parse_sap_csv, parse_utility_csv, parse_concur_json

from django.db.models.functions import TruncMonth

class DashboardStatsView(APIView):
    def get(self, request):
        tenant_id = request.query_params.get('tenant')
        qs = NormalizedEmissionRecord.objects.all()
        if tenant_id:
            qs = qs.filter(tenant_id=tenant_id)
            
        total_emissions = qs.filter(status='APPROVED').aggregate(Sum('calculated_emissions'))['calculated_emissions__sum'] or Decimal('0')
        pending_count = qs.filter(status='PENDING').count()
        failed_uploads = RawDataUpload.objects.filter(status='FAILED').count()
        
        # Aggregations for charts
        approved_qs = qs.filter(status='APPROVED')
        
        scope_agg = approved_qs.values('scope').annotate(total=Sum('calculated_emissions'))
        cat_agg = approved_qs.values('category').annotate(total=Sum('calculated_emissions'))
        
        # Time series aggregation
        time_agg = approved_qs.filter(date_start__isnull=False).annotate(
            month=TruncMonth('date_start')
        ).values('month').annotate(
            total=Sum('calculated_emissions')
        ).order_by('month')
        
        emissions_by_scope = [{'name': item['scope'].replace('SCOPE_', 'Scope '), 'value': float(item['total'] or 0)} for item in scope_agg]
        emissions_by_category = [{'name': item['category'], 'value': float(item['total'] or 0)} for item in cat_agg]
        emissions_over_time = [{'name': item['month'].strftime('%b %Y'), 'value': float(item['total'] or 0)} for item in time_agg if item['month']]
        
        return Response({
            'total_emissions_approved': total_emissions,
            'pending_reviews_count': pending_count,
            'failed_uploads_count': failed_uploads,
            'emissions_by_scope': emissions_by_scope,
            'emissions_by_category': emissions_by_category,
            'emissions_over_time': emissions_over_time
        })

class ClientListView(generics.ListAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class DataSourceListView(generics.ListAPIView):
    serializer_class = DataSourceSerializer
    def get_queryset(self):
        tenant_id = self.request.query_params.get('tenant')
        if tenant_id:
            return DataSource.objects.filter(client_id=tenant_id)
        return DataSource.objects.all()

class UploadRawDataView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        data_source_id = request.data.get('data_source_id')
        
        if not file_obj or not data_source_id:
            return Response({'error': 'Missing file or data_source_id'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            data_source = DataSource.objects.get(id=data_source_id)
        except DataSource.DoesNotExist:
            return Response({'error': 'Invalid data source'}, status=status.HTTP_404_NOT_FOUND)

        upload = RawDataUpload.objects.create(
            data_source=data_source,
            raw_file=file_obj,
            uploaded_by='Frontend Analyst',
            status='PENDING'
        )

        try:
            file_content = file_obj.read()
            records = []
            if data_source.source_type == 'SAP':
                records = parse_sap_csv(file_content, data_source.client, upload)
            elif data_source.source_type == 'UTILITY':
                records = parse_utility_csv(file_content, data_source.client, upload)
                
            # Create records and calculate emissions
            for r in records:
                ef = EmissionFactor.objects.filter(category=r['category'], unit=r['normalized_unit']).first()
                calculated = Decimal('0')
                if ef:
                    calculated = r['normalized_quantity'] * ef.value
                r['emission_factor'] = ef
                r['calculated_emissions'] = calculated
                
                NormalizedEmissionRecord.objects.create(**r)

            upload.status = 'PROCESSED'
            upload.save()
            return Response({'message': f'Successfully processed {len(records)} records.', 'upload_id': upload.id}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            upload.status = 'FAILED'
            upload.error_log = str(e)
            upload.save()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SyncConcurTravelView(APIView):
    parser_classes = (JSONParser,)

    def post(self, request, *args, **kwargs):
        data_source_id = request.data.get('data_source_id')
        payload = request.data.get('payload')
        
        if not payload or not data_source_id:
            return Response({'error': 'Missing payload or data_source_id'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            data_source = DataSource.objects.get(id=data_source_id)
        except DataSource.DoesNotExist:
            return Response({'error': 'Invalid data source'}, status=status.HTTP_404_NOT_FOUND)

        upload = RawDataUpload.objects.create(
            data_source=data_source,
            raw_payload=payload,
            uploaded_by='API Sync',
            status='PENDING'
        )

        try:
            records = parse_concur_json(payload, data_source.client, upload)
            
            # Create records and calculate emissions
            for r in records:
                ef = EmissionFactor.objects.filter(category=r['category'], unit=r['normalized_unit']).first()
                calculated = Decimal('0')
                if ef:
                    calculated = r['normalized_quantity'] * ef.value
                r['emission_factor'] = ef
                r['calculated_emissions'] = calculated
                
                NormalizedEmissionRecord.objects.create(**r)

            upload.status = 'PROCESSED'
            upload.save()
            return Response({'message': f'Successfully synced {len(records)} records from Concur.'}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            upload.status = 'FAILED'
            upload.error_log = str(e)
            upload.save()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmissionRecordListView(generics.ListAPIView):
    serializer_class = NormalizedEmissionRecordSerializer
    
    def get_queryset(self):
        qs = NormalizedEmissionRecord.objects.all().order_by('-created_at')
        status_param = self.request.query_params.get('status')
        tenant_id = self.request.query_params.get('tenant')
        if status_param:
            qs = qs.filter(status=status_param)
        if tenant_id:
            qs = qs.filter(tenant_id=tenant_id)
        return qs

class EmissionRecordDetailView(generics.RetrieveUpdateAPIView):
    queryset = NormalizedEmissionRecord.objects.all()
    serializer_class = NormalizedEmissionRecordSerializer
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.status
        old_qty = instance.normalized_quantity
        
        response = super().update(request, *args, **kwargs)
        instance.refresh_from_db()
        
        # Calculate new emissions if quantity changed
        if old_qty != instance.normalized_quantity and instance.emission_factor:
            instance.calculated_emissions = instance.normalized_quantity * instance.emission_factor.value
            instance.save()
            
        # Log Audit Trail
        action = []
        if old_qty != instance.normalized_quantity:
            action.append(f"Quantity changed from {old_qty} to {instance.normalized_quantity}")
        if old_status != instance.status:
            action.append(f"Status changed from {old_status} to {instance.status}")
            
        if action:
            AuditLog.objects.create(
                record=instance,
                changed_by='Analyst (Frontend)',
                action=' | '.join(action),
                previous_state={'status': old_status, 'quantity': str(old_qty)},
                new_state={'status': instance.status, 'quantity': str(instance.normalized_quantity)}
            )
            
        return response
