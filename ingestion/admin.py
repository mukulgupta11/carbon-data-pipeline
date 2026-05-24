from django.contrib import admin
from .models import Client, DataSource, EmissionFactor, RawDataUpload, NormalizedEmissionRecord, AuditLog

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('client', 'source_type', 'created_at')
    list_filter = ('source_type', 'client')

@admin.register(EmissionFactor)
class EmissionFactorAdmin(admin.ModelAdmin):
    list_display = ('category', 'unit', 'value')

@admin.register(RawDataUpload)
class RawDataUploadAdmin(admin.ModelAdmin):
    list_display = ('data_source', 'uploaded_at', 'status', 'uploaded_by')
    list_filter = ('status', 'data_source')

@admin.register(NormalizedEmissionRecord)
class NormalizedEmissionRecordAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'category', 'scope', 'date_start', 'normalized_quantity', 'normalized_unit', 'calculated_emissions', 'status')
    list_filter = ('status', 'category', 'scope', 'tenant')
    search_fields = ('original_reference_id', 'activity_type')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('record', 'action', 'changed_by', 'changed_at')
    list_filter = ('action', 'changed_by')
