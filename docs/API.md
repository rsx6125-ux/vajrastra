# Local API

Base URL: `http://127.0.0.1:8000`. All writes require `Content-Type: application/json`; only matching local Origins are accepted when present. Unexpected Host values are rejected. Errors return an HTTP error status and `{"error":"explanation"}`. Maximum request size is below 12 MiB; decoded files are limited to 8 MiB.

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/api/bootstrap` | GET | Service catalog, applications, document metadata, preferences, mode and OCR availability |
| `/api/settings` | POST | Save `language`, `largeText`, `contrast`, `spoken` |
| `/api/documents` | POST | Upload `name`, `kind`, `mime`, base64 `content` |
| `/api/documents/{id}` | GET | Download stored document |
| `/api/documents/delete` | POST | Delete unattached document by `id` |
| `/api/ocr` | POST | Extract text from an image document by `id`, using optional Tesseract |
| `/api/applications` | POST | Create/update draft using `service`, `fields`, `documents`, optional `id` |
| `/api/applications/delete` | POST | Delete a Draft by `id` |
| `/api/applications/submit` | POST | Validate and save to demo queue; requires `id`, `consent: true` |
| `/api/applications/simulate` | POST | Demo decision using `id`, `status`, optional `reason` |
| `/api/chat` | POST | Reply to `message` in `language` (`en`, `hi`, `te`) |

Application `fields`: `name`, `phone`, `district`, `address`, `details`. Documents are stored IDs, and required document kinds come from the service catalog. Grievances require at least 20 characters of details. Drafts may be incomplete. Submission requires a two-character name, a 10-digit Indian-format mobile number, district, address, required document categories, and consent. These checks validate structure only.

State transitions: `Draft → In review → Completed` or `In review → Needs correction → In review`. Only drafts/corrections can be edited, only drafts deleted, and only applications in review can receive demo decisions. Correction reasons are mandatory. Duplicate submissions are rejected. A process lock serializes writes and SQLite commits persist data between restarts.

This API has no user authentication and is exclusively for the single-user loopback demo. It must not be publicly exposed.
