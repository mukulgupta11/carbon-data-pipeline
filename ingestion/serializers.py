from rest_framework import serializers
from .models import Client, DataSource, EmissionFactor, RawDataUpload, NormalizedEmissionRecord, AuditLog

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = '__all__'

class RawDataUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawDataUpload
        fields = '__all__'

class NormalizedEmissionRecordSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    class Meta:
        model = NormalizedEmissionRecord
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'
