# Sources Research & Sample Data Justification

## 1. SAP (Fuel and Procurement)
**Research:** SAP exports (when not using OData/BAPI) typically happen via ALV Grid downloads to Excel/CSV. These files often mix languages (depending on user locale) and use legacy plant codes.
**Sample Data (`sap_export.csv`):** 
- Uses German headers: `Belegdatum` (Doc Date), `Menge` (Quantity), `ME` (Unit), `Werk` (Plant).
- Uses non-standard units (`GAL` for gallons, `ST` for pieces).
- **What would break in reality:** A real ALV export often has merged header rows or trailing summary rows that would break a naive CSV parser. The parser would need logic to skip non-tabular rows.

## 2. Utility Data (Electricity)
**Research:** Portal exports from energy providers (like PG&E) usually provide interval data. Often, instead of providing "kWh consumed", they provide the raw meter index (the dial reading) at specific dates.
**Sample Data (`utility_bill.csv`):**
- Contains `MeterID`, `Date`, and `Index(kWh)`.
- The parser explicitly calculates consumption by subtracting the previous row's index from the current row's index.
- **What would break in reality:** Meter resets (the dial rolls over to 0) or meter replacements would result in a negative delta. The parser currently treats negative deltas as 0, but a real system requires a manual override flag for meter replacements.

## 3. Corporate Travel (Concur/Navan)
**Research:** Concur exposes the "Itinerary v4 API". It returns deeply nested JSON where `trips` contain `bookings` which contain `segments` (Air, Hotel, Car).
**Sample Data (`concur_trip.json`):**
- A simplified JSON structure mimicking the Itinerary API, with an array of trips containing `airDetails` and `hotelDetails`.
- **What would break in reality:** Flights often have layovers resulting in multiple "segments" under one ticket. The parser would need to aggregate the distances of all segments. Additionally, pagination is required for the Concur API, which is not implemented in the prototype's mock fetch.
