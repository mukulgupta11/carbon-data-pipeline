import csv
import io
import json
from datetime import datetime
from decimal import Decimal
from django.utils.timezone import make_aware

def _safe_decimal(val, default='0'):
    try:
        # handle european formats if needed, or simple commas
        val = val.replace(',', '')
        return Decimal(val)
    except:
        return Decimal(default)

def parse_sap_csv(file_content, tenant, source_upload):
    # Simulates parsing an ALV Grid CSV export for fuel and goods.
    # Columns expected (in German/English mix): 
    # Belegdatum (Doc Date), Material, Werk (Plant), Menge (Quantity), ME (Unit)
    
    csv_file = io.StringIO(file_content.decode('utf-8'))
    reader = csv.DictReader(csv_file)
    records = []
    
    for row in reader:
        try:
            # Inconsistent date formats: assume DD.MM.YYYY
            date_str = row.get('Belegdatum') or row.get('DocDate')
            if date_str:
                dt = datetime.strptime(date_str.strip(), '%d.%m.%Y')
                dt = make_aware(dt)
            else:
                dt = None

            quantity = _safe_decimal(row.get('Menge', '0'))
            unit = row.get('ME', '').strip().upper()
            material = row.get('Material', '').strip()
            plant = row.get('Werk', '').strip()

            # Normalization logic
            normalized_qty = quantity
            normalized_unit = unit
            category = 'Other'
            scope = 'SCOPE_3'

            if material.lower() in ['diesel', 'fuel']:
                category = 'Diesel Fuel'
                scope = 'SCOPE_1'
                if unit == 'GAL':
                    normalized_qty = quantity * Decimal('3.78541')
                    normalized_unit = 'Liters'
                elif unit == 'L':
                    normalized_unit = 'Liters'

            records.append({
                'original_reference_id': row.get('DocNum', f"SAP-{plant}-{date_str}"),
                'category': category,
                'scope': scope,
                'activity_type': f"Purchased {material} at {plant}",
                'date_start': dt,
                'date_end': dt,
                'raw_quantity': quantity,
                'raw_unit': unit,
                'normalized_quantity': normalized_qty,
                'normalized_unit': normalized_unit,
                'tenant': tenant,
                'source_upload': source_upload,
                'status': 'PENDING'
            })
        except Exception as e:
            print(f"Error parsing SAP row: {e}")
            continue
    return records


def parse_utility_csv(file_content, tenant, source_upload):
    # Simulates parsing a Utility Portal CSV with cumulative index
    # Columns: MeterID, Date, Index(kWh), Status
    csv_file = io.StringIO(file_content.decode('utf-8'))
    reader = csv.DictReader(csv_file)
    
    # Needs sorting by date to calculate difference
    rows = list(reader)
    rows.sort(key=lambda r: datetime.strptime(r['Date'].strip(), '%Y-%m-%d'))

    records = []
    previous_index = None
    previous_date = None

    for row in rows:
        try:
            dt = make_aware(datetime.strptime(row['Date'].strip(), '%Y-%m-%d'))
            current_index = _safe_decimal(row['Index(kWh)'])
            meter_id = row.get('MeterID', 'UNKNOWN_METER')

            if previous_index is not None:
                consumption = current_index - previous_index
                if consumption < 0:
                    consumption = Decimal('0') # Handle meter resets or replacements
                
                records.append({
                    'original_reference_id': f"{meter_id}-{dt.strftime('%Y%m%d')}",
                    'category': 'Grid Electricity',
                    'scope': 'SCOPE_2',
                    'activity_type': f"Electricity Consumption ({meter_id})",
                    'date_start': previous_date,
                    'date_end': dt,
                    'raw_quantity': consumption,
                    'raw_unit': 'kWh',
                    'normalized_quantity': consumption,
                    'normalized_unit': 'kWh',
                    'tenant': tenant,
                    'source_upload': source_upload,
                    'status': 'PENDING'
                })
            
            previous_index = current_index
            previous_date = dt
        except Exception as e:
            print(f"Error parsing Utility row: {e}")
            continue
    return records

def parse_concur_json(payload, tenant, source_upload):
    # Simulates Concur Trip/Itinerary parsing
    records = []
    
    trips = payload.get('data', [])
    for trip in trips:
        trip_id = trip.get('id')
        
        # Parse Air Details
        air = trip.get('airDetails')
        if air:
            # We would normally compute distance between airport codes. For now, dummy logic.
            dt = None
            if air.get('departureDate'):
                dt = datetime.fromisoformat(air['departureDate'].replace('Z', '+00:00'))
            
            dist = Decimal('1000') # Dummy distance
            if air.get('distance'):
                dist = Decimal(air['distance'])

            records.append({
                'original_reference_id': air.get('ticketNumber', trip_id),
                'category': 'Flight (Short Haul)',
                'scope': 'SCOPE_3',
                'activity_type': f"Flight on {air.get('airline', 'Unknown')}",
                'date_start': dt,
                'date_end': dt,
                'raw_quantity': dist,
                'raw_unit': 'km',
                'normalized_quantity': dist,
                'normalized_unit': 'km',
                'tenant': tenant,
                'source_upload': source_upload,
                'status': 'PENDING'
            })
            
        # Parse Hotel Details
        hotel = trip.get('hotelDetails')
        if hotel:
            try:
                checkin = datetime.strptime(hotel['hotelCheckinDate'], '%Y-%m-%d')
                checkout = datetime.strptime(hotel['hotelCheckoutDate'], '%Y-%m-%d')
                nights = (checkout - checkin).days
                if nights <= 0:
                    nights = 1
                
                records.append({
                    'original_reference_id': f"{trip_id}-HOTEL",
                    'category': 'Hotel Stay',
                    'scope': 'SCOPE_3',
                    'activity_type': f"Hotel Stay at {hotel.get('propertyName')}",
                    'date_start': make_aware(checkin),
                    'date_end': make_aware(checkout),
                    'raw_quantity': Decimal(nights),
                    'raw_unit': 'Nights',
                    'normalized_quantity': Decimal(nights),
                    'normalized_unit': 'Nights',
                    'tenant': tenant,
                    'source_upload': source_upload,
                    'status': 'PENDING'
                })
            except Exception as e:
                print(f"Error parsing hotel: {e}")

    return records
