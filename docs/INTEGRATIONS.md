# Integration boundaries

## Optional AI gateway (implemented)

Set `ASSISTANT_GATEWAY_URL` to a trusted HTTPS endpoint and `ASSISTANT_GATEWAY_TOKEN` to its server-side bearer token. The app sends only each assistant message and chosen language to that endpoint. Enabling this intentionally sends chat text outside the computer; disclose that to users and configure an appropriate data policy before using real information. The browser never receives the token. Timeout is 25 seconds; errors are shown without exposing credentials.

Request:

```json
{"message":"I need a pension renewal","language":"en"}
```

Expected response:

```json
{"reply":"I can help you prepare a pension renewal.","services":["pension"]}
```

Recognized service IDs: `income`, `residence`, `pension`, `disability`, `health`, `license`, `grievance`, `benefit`. Unknown service IDs are discarded. Replies are displayed as text, never executable HTML. The assistant cannot submit applications or change stored records through this contract.

## Bhashini / VoicERA (not connected)

The abstract proposes these technologies. This delivery uses browser speech recognition and synthesis so the demonstration can run without credentials. No Bhashini endpoint, model ID or auth scheme is invented. For a direct integration, obtain the authorized API specification and credentials, implement a server-side speech adapter, define audio size/duration limits and language selection, and replace the `microphone`/`speak` browser implementation. Preserve visible text fallback and citizen review. Do not embed credentials in public JavaScript.

## Government submission (not connected)

`/api/applications/submit` deliberately writes only a local demo event. Do not relabel it as a live submission. A live adapter requires an authorized service provider agreement, accurate state/district-specific schema, current fee and checklist source, authentication requirements, and official response/status contract.

A production implementation should separate draft preparation from actual submission and should record: citizen consent, exact reviewed payload, a unique idempotency key, integration identity, official acknowledgement, timestamps, failures and retries. Service-specific OTP/biometric/in-person requirements must remain in their authorized flow. Never auto-resubmit after a correction without renewed citizen review and authorization.

Status changes in this edition are explicitly user-triggered simulations. Replace them with authenticated official polling/webhook processing when a service contract exists. Introduce a `Pending verification` state as required by the provider; do not treat local form checks as identity verification.

## Before a public multi-user deployment

Replace the local HTTP server with a production service, add authenticated user ownership checks for every record and document, TLS, encrypted storage, retention/deletion controls, malware scanning, auditable consent, upload quotas and rate limits. Remove public demo-decision controls from citizen roles. Test translations with native speakers and accessibility with intended users. Pin verified department service configurations and integrate official payment handling only when authorized. This package intentionally does not simulate an official OTP, biometric result, issued certificate or payment success.
