# Decisions & Ambiguities Resolved

This document outlines the major decisions made while scoping and building this prototype.

## 1. Subsets of Data Handled
The PM prompt asks to handle three massive domains (SAP, Utility, Travel). To build a focused, high-quality prototype, I scoped the ingestion to highly realistic, specific subsets:

- **SAP (Fuel & Procurement):** I modeled an ALV Grid CSV export. SAP exports are notoriously messy. I decided to handle **Diesel Purchases (Scope 1)** and **General Office Supplies (Scope 3)**. The parser explicitly handles German column headers (`Menge`, `ME`) and inconsistent European date formats (`DD.MM.YYYY`).
- **Utility Data:** Modeled as a Monthly CSV Export from a utility portal (Scope 2). I resolved the ambiguity of "how is usage reported" by assuming the hardest common case: the CSV reports *cumulative meter index readings*, requiring the parser to compute the delta (consumption) between rows.
- **Corporate Travel:** Modeled as a JSON push from the Concur Itinerary API (v4). The ambiguity was "how does this data arrive?" I decided to simulate a Webhook/API sync rather than a file upload, as enterprise travel systems are typically integrated via API.

## 2. Ingestion Mechanism
- **SAP / Utility:** File Upload. Sustainability leads generally do not have API access to ERPs; they are emailed CSV exports.
- **Travel:** API Sync. Concur/Navan are modern platforms where server-to-server integration is standard.

## 3. Asynchronous Processing vs Synchronous
For this prototype, file parsing happens synchronously during the request cycle. In a production environment with massive SAP dumps, this would be offloaded to Celery. I chose synchronous parsing here to minimize deployment complexity and ensure immediate UI feedback for the analyst.

## 4. What I'd ask the PM
- **Deduplication:** "If a client uploads the same SAP export twice, should we blindly duplicate, reject the whole file, or upsert based on the `DocNum`?"
- **Billing Periods vs Calendar Months:** "Utility bills often span e.g. Jan 14 to Feb 14. Should we allocate emissions proportionally across the two months, or just tag it to the billing cycle end date?" (I chose to store `date_start` and `date_end` to defer this decision to the reporting layer).
