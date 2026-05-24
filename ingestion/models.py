from django.db import models
from django.utils import timezone
import uuid

class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DataSource(models.Model):
    SOURCE_CHOICES = [
        ('SAP', 'SAP'),
        ('UTILITY', 'Utility Bill'),
        ('TRAVEL', 'Corporate Travel API')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='data_sources')
    source_type = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    connection_details = models.JSONField(blank=True, null=True) # e.g. Plant mappings, credentials
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.name} - {self.get_source_type_display()}"

class EmissionFactor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=100) # e.g. 'Grid Electricity', 'Diesel', 'Flight'
    unit = models.CharField(max_length=50)      # e.g. 'kWh', 'Liters', 'km'
    value = models.DecimalField(max_digits=15, decimal_places=6) # kg CO2e per unit
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.category} ({self.unit}) -> {self.value} kg CO2e"

class RawDataUpload(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSED', 'Processed'),
        ('FAILED', 'Failed')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='uploads')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.CharField(max_length=255, default='System')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    raw_file = models.FileField(upload_to='uploads/%Y/%m/', blank=True, null=True)
    raw_payload = models.JSONField(blank=True, null=True) # For API payloads
    error_log = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Upload {self.id} for {self.data_source} at {self.uploaded_at.date()}"

class NormalizedEmissionRecord(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    ]
    SCOPE_CHOICES = [
        ('SCOPE_1', 'Scope 1'),
        ('SCOPE_2', 'Scope 2'),
        ('SCOPE_3', 'Scope 3')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='emission_records')
    source_upload = models.ForeignKey(RawDataUpload, on_delete=models.SET_NULL, null=True, related_name='parsed_records')
    original_reference_id = models.CharField(max_length=255, blank=True, null=True) # SAP Doc No, Flight PNR, Meter ID

    category = models.CharField(max_length=100) # Fuel, Electricity, Flight, Hotel
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    activity_type = models.CharField(max_length=255) # e.g. 'Stationary Combustion', 'Business Travel'
    
    date_start = models.DateTimeField(blank=True, null=True)
    date_end = models.DateTimeField(blank=True, null=True)

    raw_quantity = models.DecimalField(max_digits=20, decimal_places=6, blank=True, null=True)
    raw_unit = models.CharField(max_length=50, blank=True, null=True)

    normalized_quantity = models.DecimalField(max_digits=20, decimal_places=6, blank=True, null=True)
    normalized_unit = models.CharField(max_length=50, blank=True, null=True) # Usually kWh or Liters/km

    emission_factor = models.ForeignKey(EmissionFactor, on_delete=models.SET_NULL, null=True, blank=True)
    calculated_emissions = models.DecimalField(max_digits=20, decimal_places=6, blank=True, null=True) # in kg CO2e

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reviewer_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category} - {self.calculated_emissions} kg CO2e ({self.status})"

class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(NormalizedEmissionRecord, on_delete=models.CASCADE, related_name='audit_logs')
    changed_by = models.CharField(max_length=255)
    changed_at = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=255) # e.g., 'Status Changed to Approved', 'Quantity Edited'
    previous_state = models.JSONField(blank=True, null=True)
    new_state = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.action} by {self.changed_by} on {self.changed_at}"
