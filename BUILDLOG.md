# BUILDLOG.md

- AI Assistance: Used generative models to stub out the FastAPI boilerplate and the CORS middleware configuration.
- Adjustments: Hand-coded the `httpx` async fallback chain for geolocation to ensure it degraded gracefully without blocking the 201 Created response. Added the `slowapi` dependency for clean in-memory rate limiting.
