# API Specs

Once you send your submission for evaluation, you can have your app tested against some tests we developed to ensure your application complies with the features of a basic URL shortener. This doesn't replace the tests you might come up with your team, but can help you work towards the reliability quest!

**PS:** There are some tests that have their input/output hidden for you. We can't tell you as that would be too easy, but if your app handles edge cases, you might pass them! We will share hints as the hackathon goes on.

---

## Test Endpoints

### 1. Health

Ensure your API is running and ready to accept requests.

- **Endpoint:** `GET /health`
- **Input Payload:** None
- **Expected Response:** `200 OK`
- **Response Format:**

  ```json
  {
    "status": "ok"
  }
  ```

---

### 2. Users

#### Bulk Load Users (CSV Import)

- **Endpoint:** `POST /users/bulk`
- **Input Payload:** `multipart/form-data` with a `file` field containing `users.csv`
- **Expected Response:** `200 OK` or `201 Created`
- **Response Format:** Must indicate the number of imported users. Acceptable formats include:

  ```json
  { "count": 2 }
  ```

  ```json
  { "imported": 2 }
  ```

  Or simply returning an array of imported objects.

#### List Users

- **Endpoint:** `GET /users`
- **Input Payload:** None (Query parameters `?page=x&per_page=y` should optionally paginate results)
- **Expected Response:** `200 OK`
- **Response Format:** A JSON array of users (or a paginated envelope like `{"users": [...]}`)

  ```json
  [
    {
      "id": 1,
      "username": "silvertrail15",
      "email": "silvertrail15@hackstack.io",
      "created_at": "2025-09-19T22:25:05"
    },
    {
      "id": 2,
      "username": "urbancanyon36",
      "email": "urbancanyon36@opswise.net",
      "created_at": "2024-04-09T02:51:03"
    }
  ]
  ```

#### Get User by ID

- **Endpoint:** `GET /users/<id>`
- **Input Payload:** None
- **Expected Response:** `200 OK`
- **Response Format:** Single JSON user object for `<id>`

  ```json
  {
    "id": 1,
    "username": "silvertrail15",
    "email": "silvertrail15@hackstack.io",
    "created_at": "2025-09-19T22:25:05"
  }
  ```

#### Create User

- **Endpoint:** `POST /users`
- **Input Payload:**

  ```json
  {
    "username": "testuser",
    "email": "testuser@example.com"
  }
  ```

- **Expected Response:** `201 Created`
- **Response Format:** The created user object. The endpoint must reject invalid data schemas (e.g., integer for username) and return `400 Bad Request` or `422 Unprocessable Entity` containing an error dictionary.

  ```json
  {
    "id": 3,
    "username": "testuser",
    "email": "testuser@example.com",
    "created_at": "2026-04-03T12:00:00"
  }
  ```

#### Update User

- **Endpoint:** `PUT /users/<id>`
- **Input Payload:**

  ```json
  {
    "username": "updated_username"
  }
  ```

- **Expected Response:** `200 OK`
- **Response Format:** The updated user object

  ```json
  {
    "id": 1,
    "username": "updated_username",
    "email": "silvertrail15@hackstack.io",
    "created_at": "2025-09-19T22:25:05"
  }
  ```

---

### 3. URLs

#### Create URL

- **Endpoint:** `POST /urls`
- **Input Payload:**

  ```json
  {
    "user_id": 1,
    "original_url": "https://example.com/test",
    "title": "Test URL"
  }
  ```

- **Expected Response:** `201 Created`
- **Response Format:** URL object containing the generated `short_code`. Should handle missing user gracefully and throw errors for invalid constraints.

  ```json
  {
    "id": 3,
    "user_id": 1,
    "short_code": "k8Jd9s",
    "original_url": "https://example.com/test",
    "title": "Test URL",
    "is_active": true,
    "created_at": "2026-04-03T12:00:00",
    "updated_at": "2026-04-03T12:00:00"
  }
  ```

#### List URLs

- **Endpoint:** `GET /urls`
- **Input Payload:** None (Should accept filtering queries like `?user_id=1`)
- **Expected Response:** `200 OK`
- **Response Format:** A JSON array of URL objects

  ```json
  [
    {
      "id": 1,
      "user_id": 1,
      "short_code": "ALQRog",
      "original_url": "https://opswise.net/harbor/journey/1",
      "title": "Service guide lagoon",
      "is_active": true,
      "created_at": "2025-06-04T00:07:00",
      "updated_at": "2025-11-19T03:17:29"
    }
  ]
  ```

#### Get URL by ID

- **Endpoint:** `GET /urls/<id>`
- **Input Payload:** None
- **Expected Response:** `200 OK`
- **Response Format:** Single URL object matching the `<id>`

  ```json
  {
    "id": 1,
    "user_id": 1,
    "short_code": "ALQRog",
    "original_url": "https://opswise.net/harbor/journey/1",
    "title": "Service guide lagoon",
    "is_active": true,
    "created_at": "2025-06-04T00:07:00",
    "updated_at": "2025-11-19T03:17:29"
  }
  ```

#### Update URL Details

- **Endpoint:** `PUT /urls/<id>`
- **Input Payload:**

  ```json
  {
    "title": "Updated Title",
    "is_active": false
  }
  ```

- **Expected Response:** `200 OK`
- **Response Format:** The updated URL object

  ```json
  {
    "id": 1,
    "user_id": 1,
    "short_code": "ALQRog",
    "original_url": "https://opswise.net/harbor/journey/1",
    "title": "Updated Title",
    "is_active": false,
    "created_at": "2025-06-04T00:07:00",
    "updated_at": "2026-04-03T12:00:00"
  }
  ```

---

### 4. Events / Analytics

#### List Events

- **Endpoint:** `GET /events`
- **Input Payload:** None
- **Expected Response:** `200 OK`
- **Response Format:** A JSON array of Event objects

  ```json
  [
    {
      "id": 1,
      "url_id": 1,
      "user_id": 1,
      "event_type": "created",
      "timestamp": "2025-06-04T00:07:00",
      "details": {
        "short_code": "ALQRog",
        "original_url": "https://opswise.net/harbor/journey/1"
      }
    }
  ]
  ```

---

### 5. Operational Endpoints

#### Metrics

- **Endpoint:** `GET /metrics`
- **Input Payload:** None
- **Expected Response:** `200 OK`
- **Response Format:** Process and system resource usage snapshot

  ```json
  {
    "cpu_percent": 8.2,
    "system_ram": {
      "used_gb": 6.4,
      "total_gb": 15.9
    },
    "process_memory_mb": 91.7
  }
  ```

#### Logs

- **Endpoint:** `GET /logs`
- **Input Payload:** None
- **Expected Response:** `200 OK`
- **Response Format:** Recent structured log records

  ```json
  {
    "logs": [
      {
        "timestamp": "2026-04-04T12:00:00+00:00",
        "level": "INFO",
        "logger": "app",
        "message": "Health check requested",
        "method": "GET",
        "path": "/health",
        "remote_addr": "127.0.0.1"
      }
    ]
  }
  ```

## What changed

### 1) Response schema is now more flexible

Your API responses may now include additional fields/metadata without being penalized.

- Extra keys are allowed.
- Additional wrapper objects are allowed.
- The tests now focus on whether the required data points are present and correct. These required data points come from the seed files that you can download from your team page.

### 2) Nested response shapes are accepted

For checks like `id`, `user_id`, `url_id`, `event_type`, `is_active`, and `short_code`, tests now support values that appear in nested objects (not only top-level fields).

### 3) Better participant diagnostics

Failure diagnostics shown were improved so they better reflect nested/wrapped response payloads and reduce false mismatch messages.

## What did NOT change

- Endpoint behavior requirements remain the same.
- Status code expectations remain the same.
- Hidden challenge tests are still hidden and shown as **Advanced challenge #N**. We will be sharing hints very very soon.

## Do you need to change your submission?

**Not necessarily.**

If your API already returns the required values, even with additional fields or nesting, you should be in better shape with the updated tests.

## Effective scope

These updates apply to new evaluations/reruns. Existing completed evaluations are unchanged.

## Example (now accepted)

If a test expects `id: 1`, these can both be valid:

```json
{ "id": 1 }
```

```json
{ "data": { "user": { "id": 1, "extra": "ok" } } }
```

Likewise, list/filter checks can pass when fields appear in nested sample records.

## Need help?

If your latest run still fails and the feedback looks unclear, create a post on the Q&A section on this platform with this information:

- endpoint tested,
- expected behavior,
- your actual response payload,
- and the reported diagnostic message.
