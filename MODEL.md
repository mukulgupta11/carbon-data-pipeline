# Data Model

The data model for Breathe ESG's ingestion prototype is designed to be highly flexible, auditable, and multi-tenant-ready. It decouples the *raw ingestion layer* from the *normalized emission record*, ensuring a clear source-of-truth.

## Core Entities

### 1. `Client` (Multi-Tenancy)
- `id` (UUID), `name`
- **Why:** To support multi-tenancy inherently. All subsequent data sources and emission records trace back to a specific `Client`.

### 2. `DataSource` (Source-of-Truth Tracking)
- `id` (UUID), `client_id`, `source_type` (SAP, UTILITY, TRAVEL)
- **Why:** Real-world clients have multiple ERP instances or utility providers. We need to know *which* system a record originated from.

### 3. `RawDataUpload` (Auditability & Re-processing)
- `id`, `data_source_id`, `raw_file`, `raw_payload`, `status`
- **Why:** If the normalization logic changes or an error occurs, we must be able to re-process the exact raw bytes we received. This acts as an immutable ledger of all inbound data.

### 4. `NormalizedEmissionRecord` (The Core Ledger)
- `tenant_id`, `source_upload_id` (FK to RawDataUpload)
- `original_reference_id`: (e.g., SAP DocNum, Flight PNR). Vital for deduplication and traceback.
- `category` & `scope`: Categorization (Scope 1/2/3).
- `date_start`, `date_end`: Handles billing periods (utility bills) vs. point-in-time transactions (fuel purchase).
- `raw_quantity` & `raw_unit`: Exactly what the source system reported.
- `normalized_quantity` & `normalized_unit`: Converted to a standard metric (e.g. Gallons -> Liters).
- `calculated_emissions`: The final computed `kg CO2e`.
- `status`: Pending, Approved, Rejected.

### 5. `AuditLog` (Compliance)
- `record_id`, `changed_by`, `action`, `previous_state`, `new_state`
- **Why:** Before a row is "locked for audit", analysts will tweak quantities (e.g., removing personal miles from a corporate flight). Every state transition and quantity edit is logged as a JSON diff.

### 6. `EmissionFactor`
- `category`, `unit`, `value` (kg CO2e)
- **Why:** A lookup table to decouple emission calculation logic from the parsing logic.

## Scope & Unit Normalization
When raw data is ingested, the parser performs a two-step mapping:
1. **Scope Mapping:** Uses business logic (e.g., "Purchased Electricity" -> Scope 2).
2. **Unit Normalization:** Normalizes imperial/legacy units to standard metric units before multiplying by the `EmissionFactor`. This guarantees uniform calculations across varying client setups.
