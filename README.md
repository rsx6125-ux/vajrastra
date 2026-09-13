# VAJRASTRA

A multilingual citizen-services workspace based on the supplied VAJRASTRA abstract. Responsive navy and teal UI, guided applications, voice interaction, local document management, SQLite persistence, and a complete demonstration review workflow.

## Start the app

**Windows:** Extract the ZIP, open the `vajrastra` folder, and double-click **START.bat**. Keep the terminal window open. It uses Python 3 or the Codex bundled Python available on this computer.

**Any platform with Python 3.10+:**

```sh
python run.py
```

On macOS/Linux, use `python3 run.py` if needed. Your browser opens at **http://127.0.0.1:8000**. No npm install, pip install, API key, database setup, or build step is needed. Do not open `public/index.html` directly: it needs the server.

To run without automatically opening a browser:

```sh
python server.py
```

The browser-opening launcher tries the next available port if 8000 is occupied (up to 8009). The headless `server.py` command uses the configured port only. You can also set `PORT` before launching. For PowerShell: `$env:PORT = '8001'`.

## Included features

- Dashboard with real local counts and recent applications; no invented citizen records.
- Eight example services: income and residence certificates, pension renewal, disability certificates, healthcare enrollment, license renewal, grievances, and welfare scheme applications.
- Service search and category filtering.
- Three-step application flow: details, reusable documents, and review with explicit consent.
- Browser voice input and speech playback; English, Hindi and Telugu navigation, service names, forms, and local guide replies.
- SQLite-backed drafts, application status, event history, document storage and preferences.
- PNG/JPG/PDF uploads with size and signature checks; document downloads and deletion of unused documents.
- Optional local image OCR with reviewable extracted text.
- Demo submission, completion, correction reasons and resubmission, retaining history.
- Application search/status filters and downloadable plain-text receipts.
- Large text, higher contrast, reduced-motion support, keyboard focus, native dialogs, mobile layout, and text fallback for speech.
- Optional server-side HTTPS assistant gateway with credentials kept out of the browser.

## Try a complete workflow

1. Open **Explore services → File a grievance**.
2. Use a fictitious name, a sample 10-digit number starting with 6–9, and a sample district/address. Write a grievance description of at least 20 characters. No uploads are mandatory for this example.
3. Continue to documents, then review. Try the read-aloud control if your device supports speech.
4. Check the consent box and select **Send to demo queue**.
5. In the application detail, choose **Simulate correction** and enter a sample reason.
6. Continue the application, make a correction, review and resubmit. The history records both submissions.
7. Choose **Simulate completion** and download a receipt.
8. Try a certificate application with sample files for its required document types. Saved documents can be selected again.

## What requires an external integration

This package is a complete **local demonstration**, not a live government gateway. It does not submit to government portals, issue certificates, check eligibility, take payments, verify identity, perform biometrics/OTP, or provide official live status. Example fees, document lists and timelines are not official service rules. No authorization can be inferred from a successful demo submission.

The default assistant is deterministic keyword matching, not a trained AI model. Browser speech is used instead of Bhashini/VoicERA. A trusted AI gateway can be configured; direct Bhashini and government integrations are not included because their credentials, service contracts and API specifications were not supplied. See [integration notes](docs/INTEGRATIONS.md).

The main citizen journey is translated; developer/demo decision messages, help content, OCR feedback and some errors remain English. Speech recognition may depend on an internet connection and browser provider. It is not guaranteed in every browser or dialect. Speech playback depends on installed voices. Text input always works.

## OCR

Install Tesseract and place its executable on PATH. Restart the app and choose **OCR** beside a JPG/PNG. English is the default; set `OCR_LANGUAGES=eng+hin+tel` only after installing the corresponding language packs. PDF text extraction is not provided. OCR output must be manually checked and copied; it does not establish authenticity or automatically alter the application.

## Data and scope

Data lives in `data/vajrastra.db`, created on first launch. It is intentionally excluded from the code ZIP. This is a single-user local app with no account system, database encryption, or role isolation. Use fictitious information and sample files. The server binds only to loopback, rejects unexpected Host/Origin headers, uses parameterized queries, escapes UI content, and applies restrictive response headers. It is not designed to be exposed publicly.

Back up `data/` with the app stopped. To erase all records, stop the server and delete that folder. Drafts can be deleted in the UI. A document attached to any saved application cannot be deleted without first removing the associated draft; submitted record attachments are retained.

Environment variables are read directly. `.env.example` is documentation, not an automatically loaded configuration file. Keep secrets out of source control.

## Source layout

```text
vajrastra/
  START.bat               Windows launcher
  run.py                  Browser-opening launcher
  server.py               HTTP API, SQLite storage, service catalog, OCR, guide
  public/
    index.html            Application shell and metadata
    app.js                Views, translations, application state, speech
    style.css             Responsive theme and accessibility styling
    favicon.svg           VAJRASTRA mark
  tests/test_server.py    Isolated API/workflow integration tests
  docs/INTEGRATIONS.md    Gateway contract and live integration boundaries
  docs/API.md             Local API reference
  docs/VALIDATION.md      Verification record and untested dependencies
  .env.example            Optional environment settings
  requirements.txt       No Python package dependencies
```

## Tests

```sh
python -m unittest discover -s tests -v
```

Tests start a server on an available local port and use a temporary database. They cover correction/resubmission, consent, duplicate submissions, upload validation, required documents, persistence, multilingual matching, and local origin restrictions. Your saved data is not changed.

The source is intentionally dependency-free and can be edited directly. There is no generated build output to regenerate.
