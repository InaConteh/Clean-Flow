API Architecture: Develop a stateless Flask API to handle all frontend actions and SMS routing
.
SMS Handler (The Bridge): Implement a /api/sms/callback endpoint to receive POST payloads from the Africa’s Talking API
. Use regex patterns to parse incoming commands:
STATUS [ID], CAUSE [ID] [CODE], NEARBY [AREA], and TIPS
.
Response Logic: Outbound SMS must be concise (<160 characters) and use emojis (🟢, 🟡, 🔴, ✅) for instant visual comprehension
.
Prediction Engine: Build a background worker to fetch external rainfall data, analyze historical "Dry Well" report trends, and trigger automated WARNING SMS broadcasts to affected districts
.

--------------------------------------------------------------------------------
3. Data Layer & Business Logic (PostgreSQL)
Schema Design: Implement a relational PostgreSQL database with the following key tables:
water_sources: Tracks status and location (Latitude/Longitude)
.
reports: Logs community-reported issues across 6 categories (Drought, Broken Pump, Contamination, etc.)
.
maintenance_logs: Schedules proactive tasks like pump lubrication
.
repair_cases: Links reports to technical teams and tracks ETAs
.
Integrity: Use SQL Parameterization for all queries to prevent injection attacks
.

--------------------------------------------------------------------------------
4. Infrastructure & Security
Deployment: Containerize the application using Docker for consistency
. Use Gunicorn as the web server and Nginx as a reverse proxy for SSL and static files
.
Security Protocols: Implement rate limiting on the SMS callback endpoint to prevent spam/DOS attacks
. Ensure no Personally Identifiable Information (PII) is stored for anonymous reporters
.
Reliability: The system must maintain 99.9% uptime for the SMS gateway and be scalable to handle up to 10,000 water points nationwide
.

--------------------------------------------------------------------------------
Execution Instructions:
Phase 1: Initialize the PostgreSQL schema and Flask API skeleton.
Phase 2: Integrate Africa's Talking callback logic and SMS regex parser.
Phase 3: Develop the React Public Portal and Leaflet map integration.
Phase 4: Build the secure Admin Dashboard and Dispatch workflow.
Phase 5: Implement the Prediction Engine and automated warning alerts.