import os
import json
from decimal import Decimal
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ingestion.models import Client, DataSource, EmissionFactor, RawDataUpload, NormalizedEmissionRecord, AuditLog
from ingestion.parsers import parse_sap_csv, parse_utility_csv, parse_concur_json

def run():
    print("Seeding database and pre-populating sample data...")

    # Clear old data
    NormalizedEmissionRecord.objects.all().delete()
    RawDataUpload.objects.all().delete()

    # Create dummy client
    client, _ = Client.objects.get_or_create(name='Acme Corp (Demo Client)')
    print(f"Client: {client.name}")

    # Create Data Sources
    sap_source, _ = DataSource.objects.get_or_create(client=client, source_type='SAP', defaults={'connection_details': {'system': 'SAP ECC 6.0'}})
    utility_source, _ = DataSource.objects.get_or_create(client=client, source_type='UTILITY', defaults={'connection_details': {'provider': 'Global Power Inc'}})
    travel_source, _ = DataSource.objects.get_or_create(client=client, source_type='TRAVEL', defaults={'connection_details': {'api': 'Concur Itinerary API v4'}})

    # Create Emission Factors
    factors = [
        {'category': 'Diesel Fuel', 'unit': 'Liters', 'value': 2.68, 'description': 'Stationary Combustion - Diesel (kg CO2e per Liter)'},
        {'category': 'Grid Electricity', 'unit': 'kWh', 'value': 0.45, 'description': 'Purchased Electricity (kg CO2e per kWh)'},
        {'category': 'Flight (Short Haul)', 'unit': 'km', 'value': 0.15, 'description': 'Business Travel - Flight (kg CO2e per km)'},
        {'category': 'Hotel Stay', 'unit': 'Nights', 'value': 15.0, 'description': 'Business Travel - Hotel (kg CO2e per night)'},
    ]

    for f in factors:
        EmissionFactor.objects.get_or_create(category=f['category'], unit=f['unit'], defaults={
            'value': f['value'],
            'description': f['description']
        })

    def process_records(records, upload):
        for r in records:
            ef = EmissionFactor.objects.filter(category=r['category'], unit=r['normalized_unit']).first()
            calculated = Decimal('0')
            if ef:
                calculated = r['normalized_quantity'] * Decimal(str(ef.value))
            r['emission_factor'] = ef
            r['calculated_emissions'] = calculated
            NormalizedEmissionRecord.objects.create(**r)

    # 1. Ingest SAP Data
    with open('samples/sap_export.csv', 'rb') as f:
        upload = RawDataUpload.objects.create(data_source=sap_source, uploaded_by='System Seed', status='PROCESSED')
        records = parse_sap_csv(f.read(), client, upload)
        process_records(records, upload)

    # 2. Ingest Utility Data
    with open('samples/utility_bill.csv', 'rb') as f:
        upload = RawDataUpload.objects.create(data_source=utility_source, uploaded_by='System Seed', status='PROCESSED')
        records = parse_utility_csv(f.read(), client, upload)
        process_records(records, upload)

    # 3. Ingest Concur Data
    with open('samples/concur_trip.json', 'r') as f:
        payload = json.load(f)
        upload = RawDataUpload.objects.create(data_source=travel_source, uploaded_by='System Seed', status='PROCESSED', raw_payload=payload)
        records = parse_concur_json(payload, client, upload)
        process_records(records, upload)

    import random
    from datetime import datetime, timedelta
    from django.utils.timezone import make_aware

    # 4. Generate lots of historical data for analytics
    print("Generating historical data...")
    categories = [
        ('Diesel Fuel', 'SCOPE_1', 'Liters'),
        ('Grid Electricity', 'SCOPE_2', 'kWh'),
        ('Flight (Short Haul)', 'SCOPE_3', 'km'),
        ('Hotel Stay', 'SCOPE_3', 'Nights')
    ]
    
    now = datetime.now()
    for _ in range(2000):
        cat, scope, unit = random.choice(categories)
        ef = EmissionFactor.objects.filter(category=cat).first()
        qty = Decimal(random.randint(50, 1500))
        calc = qty * Decimal(str(ef.value)) if ef else Decimal('0')
        
        days_ago = random.randint(1, 365)
        dt = make_aware(now - timedelta(days=days_ago))
        
        NormalizedEmissionRecord.objects.create(
            tenant=client,
            original_reference_id=f"HIST-{random.randint(1000, 9999)}",
            category=cat,
            scope=scope,
            activity_type=f"Historical {cat} Usage",
            date_start=dt,
            date_end=dt,
            raw_quantity=qty,
            raw_unit=unit,
            normalized_quantity=qty,
            normalized_unit=unit,
            emission_factor=ef,
            calculated_emissions=calc,
            status='APPROVED' # Auto approve for charts
        )

    print("Seeding complete. Application is pre-populated with data!")

if __name__ == '__main__':
    run()
