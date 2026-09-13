# Validation record

Verified locally on 12 September 2026.

## Automated checks

All 10 Python integration tests passed. They cover static assets and headers, consent enforcement, duplicate-submission rejection, correction and resubmission history, immutable completed records, draft deletion, file-signature checks, required document validation and reuse, mobile-number validation, local Host/Origin restrictions, multilingual service matching, settings persistence, and unknown service/route handling. Tests use a temporary database separate from the preview and delivered source.

JavaScript syntax was checked with Node. Python modules were exercised by the integration tests and local server.

## Browser checks

- Inspected the rendered desktop dashboard, service catalog, application form, document step, review and application detail.
- Entered fictitious grievance details, proceeded through review, gave demo consent, and verified the resulting local reference and In review history.
- Uploaded a generated sample PNG through the file chooser and verified its document record and controls.
- Sent a pension request to the local assistant and verified the reply and service action.
- Switched the interface to Telugu and inspected the rendered mobile assistant at 390 × 844; document width matched viewport width, with no horizontal overflow.
- Verified the responsive navigation and returned preview preferences to English.

## Not validated against external services

No authorized government API, Bhashini account, real payment provider, official fee source, or live AI gateway was configured. These are not claimed to be tested or operational. Optional Tesseract OCR and actual microphone/audio playback depend on installed software, browser support and permission; those external capabilities were not exercised with live user audio. OCR-unavailable and speech fallback paths are included. Native speakers and intended accessibility users should review translations and usability before any real deployment.

The ZIP excludes runtime data, generated Python caches, and browser-test files. It starts with an empty citizen workspace.
