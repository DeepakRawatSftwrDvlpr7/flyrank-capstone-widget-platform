# EVIDENCE.md

## Cross-origin submissions work
The `test_origin.html` file renders the widget. Network tab confirms successful POST with CORS headers.

## Rate limiting
Sending 6 requests rapidly returns `429 Too Many Requests`.

## Spam prevention
Filling the `honeypot` payload field returns `400 Bad Request: Spam detected`.

## Geo enrichment fallback
The `httpx` async client successfully falls back to `ipapi.co` if the primary provider times out, and degrades to "Unknown" if both fail.
