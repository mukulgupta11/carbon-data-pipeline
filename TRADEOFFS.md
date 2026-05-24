# Tradeoffs

Three things deliberately NOT built in this prototype, and why:

## 1. Asynchronous Celery Workers for Parsing
**What I omitted:** Processing uploaded files via Celery queues.
**Why:** While mandatory for a real production system handling 50MB SAP dumps, introducing Redis and Celery to a 4-day prototype adds significant infrastructure overhead and complicates deployment. Synchronous parsing is sufficient to demonstrate the data model and parser logic for reasonable sample sizes.

## 2. Complex Airport Distance Calculation (Great Circle Distance)
**What I omitted:** Integrating a real API (like Google Maps or an IATA database) to calculate the exact distance between airport codes (e.g., SFO to LHR) for flight emissions.
**Why:** The objective is to demonstrate ingestion architecture, normalization, and analyst workflow. I hardcoded a dummy distance parser for the Concur API integration. Wiring up a third-party geolocation API would consume time better spent perfecting the `AuditLog` and Review Dashboard.

## 3. Granular Role-Based Access Control (RBAC)
**What I omitted:** Differentiating between "Uploader", "Analyst", and "Admin" roles via Django Groups.
**Why:** The assignment focuses on the ingestion and review flow. A complex permission matrix distracts from the core data model. I built the API assuming the caller is an authenticated "Analyst", focusing on capturing the `changed_by` string in the `AuditLog` rather than building out a full identity management UI.
