# FlyRank Capstone: Embeddable Widget Platform

A full-stack lead-generation platform adhering to the FlyRank Week 8 Capstone specifications.

## Architecture
- **Widget Delivery:** `widget.js` served with `Cache-Control` headers.
- **Submission API:** Protected by CORS middleware, `slowapi` rate limiting, and a honeypot field.
- **Enrichment:** Attempts geo-location via `ip-api.com`, falling back to `ipapi.co`.
- **Database:** SQLite handles tenant-isolated persistence.

## Run Instructions
1. Install dependencies: `pip install fastapi uvicorn slowapi httpx pydantic`
2. Run server: `uvicorn main:app --reload`
3. Test Widget: Open `test_origin.html` in your browser (acts as the second origin).
4. View Dashboard: GET `http://localhost:8000/api/dashboard` with Header `Authorization: Bearer secret-admin-token`.
