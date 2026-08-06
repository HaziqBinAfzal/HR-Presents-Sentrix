# Sentrix API Reference

## Current contract status

Sentrix RC1 is primarily a server-rendered Flask application. The repository does not yet declare a stable, versioned public REST API contract. Routes may return HTML, redirects, downloadable files, or JSON depending on implementation. Consumers must not treat internal web endpoints as a permanent external API without route-level verification and tests.

## Authentication

Browser authentication is session-based through Flask-Login. State-changing form requests are expected to use CSRF protection through Flask-WTF. An API client must preserve cookies and CSRF tokens where the route requires them.

Typical outcomes:

- `200 OK`: rendered page or successful data response
- `302 Found`: login redirect, post/redirect/get success, or navigation
- `400 Bad Request`: malformed request or validation failure
- `401 Unauthorized`: unauthenticated API-style request, when implemented
- `403 Forbidden`: authenticated user lacks access
- `404 Not Found`: route or authorized resource not found
- `413 Content Too Large`: upload exceeds configured limit
- `422 Unprocessable Content`: semantically invalid input, when implemented
- `500 Internal Server Error`: unexpected server failure

## Functional endpoint groups

The primary blueprint contains routes covering these functional groups. Exact URL rules, methods, parameter names, and response types must be generated from the running application route map before a stable API is published.

### Authentication

Registration, login, logout, email verification, forgot-password, reset-password, and related account flows.

Example browser interaction:

```http
POST /login
Content-Type: application/x-www-form-urlencoded
Cookie: session=...

email=user%40example.com&password=...&csrf_token=...
```

Expected behavior is usually a redirect with a flash message rather than a JSON token response.

### Projects

Create/upload, list, view, update metadata where supported, and delete project records. Project access must be scoped to the authenticated owner.

### Analyses and results

Start analysis, view status and findings, inspect analyzer output, and access corrected or diff artifacts where implemented. Long-running operations may currently execute within the web process; clients should not assume asynchronous job semantics unless explicitly added.

### Reports and exports

Generate or download report artifacts associated with an authorized analysis. Successful downloads should use an appropriate content type and `Content-Disposition`; missing or unauthorized artifacts should not reveal filesystem paths.

### Reviews

Create, list, view, and manage review records where supported. Inputs are untrusted and must be escaped when rendered or exported.

### History

List prior projects, analyses, or user activity exposed by the application. Pagination and retention are implementation-specific until formalized.

### Profile and settings

View and update account profile and settings. Sensitive changes should require authentication, validation, CSRF protection, and possibly password re-authentication.

### Health

A deployment may expose liveness/readiness routes, but RC1 does not guarantee their presence. Health responses must not expose secrets, stack traces, database URLs, or filesystem paths.

## Error response guidance

A future versioned JSON API should use a consistent envelope such as:

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request could not be processed.",
    "fields": {
      "project": ["A project archive is required."]
    },
    "request_id": "..."
  }
}
```

This is a target convention, not a guarantee for current HTML routes.

## Publishing a stable API

Before advertising a public API:

1. Inventory the Flask URL map and methods.
2. Separate `/api/v1` routes from browser routes.
3. Define authentication and authorization semantics.
4. Publish schemas, pagination, filtering, rate limits, idempotency, and error formats.
5. Add request/response contract tests.
6. Version breaking changes.
7. Generate OpenAPI documentation from the tested contract.
