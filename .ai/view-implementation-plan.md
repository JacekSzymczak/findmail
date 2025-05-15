# API Endpoint Implementation Plan: FindMail REST API

## 1. Endpoint Overview
| Method | Path                                              | Description                              |
| ------ | ------------------------------------------------- | ---------------------------------------- |
| POST   | /api/invitation-keys                              | Create new invitation key               |
| GET    | /api/invitation-keys                              | List all unused invitation keys         |
| DELETE | /api/invitation-keys/{key}                        | Delete a specific invitation key        |
| POST   | /api/auth/register                                | Register user with invitation key       |
| POST   | /api/auth/login                                   | Authenticate user and create session    |
| POST   | /api/auth/logout                                  | Invalidate user session                 |
| POST   | /api/mailboxes                                    | Create or access a mailbox by name      |
| POST   | /api/mailboxes/generate-random                    | Generate and register random mailbox    |
| GET    | /api/mailboxes/{name}                             | Retrieve mailbox metadata               |
| GET    | /api/mailboxes/{name}/messages                    | List messages in a mailbox              |
| GET    | /api/mailboxes/{name}/messages/{id}               | Retrieve single message content         |
| DELETE | /api/mailboxes/{name}/messages/{id}               | Permanently delete a message            |

## 2. Request Details

### 2.1 Invitation Key Management

#### Create Invitation Key
- Method: POST  
- URL: `/api/invitation-keys`  
- Required Body (JSON):
  ```json
  { "key": "string(1–32)" }
  ```
- Headers: `X-CSRF-Token`  
- Validation: non-empty, length ≤32  
- Authentication: session required  

#### List Invitation Keys
- Method: GET  
- URL: `/api/invitation-keys`  
- Authentication: session required  

#### Delete Invitation Key
- Method: DELETE  
- URL: `/api/invitation-keys/{key}`  
- Path param:
  - `key`: string (1–32)  
- Authentication: session required  

### 2.2 Authentication

#### Register
- Method: POST  
- URL: `/api/auth/register`  
- Body (JSON):
  ```json
  {
    "email": "valid_email",
    "password": "string(1–20)",
    "invitationKey": "string(1–32)"
  }
  ```
- Validation:
  - `email`: email format, ≤254  
  - `password`: non-empty, ≤20  
  - `invitationKey`: non-empty, ≤32  
- Authentication: none  

#### Login
- Method: POST  
- URL: `/api/auth/login`  
- Body (JSON):
  ```json
  { "email": "valid_email", "password": "string(1–20)" }
  ```
- Validation: as above  
- Authentication: none  

#### Logout
- Method: POST  
- URL: `/api/auth/logout`  
- Authentication: session required  

### 2.3 Mailboxes

#### Create Mailbox (Manual)
- Method: POST  
- URL: `/api/mailboxes`  
- Body (JSON):
  ```json
  { "name": "regex /^[A-Za-z0-9._%+-]{1,20}$/" }
  ```
- Validation: regex + ≤20 chars  
- Authentication: session required  

#### Generate Random Mailbox
- Method: POST  
- URL: `/api/mailboxes/generate-random`  
- No body  
- Authentication: session required  

#### View Mailbox Details
- Method: GET  
- URL: `/api/mailboxes/{name}`  
- Path param:
  - `name`: regex `/^[A-Za-z0-9._%+-]{1,20}$/`  
- Authentication: session required  

### 2.4 Messages

#### List Messages
- Method: GET  
- URL: `/api/mailboxes/{name}/messages`  
- Path param:
  - `name` (as above)  
- Query params:
  - `page` (int ≥1, default=1)  
  - `pageSize` (int 1–100, default=20)  
  - `sort` (`asc` or `desc`, default=`desc`)  
- Authentication: session required  

#### View Message
- Method: GET  
- URL: `/api/mailboxes/{name}/messages/{id}`  
- Path params:
  - `name` (as above)  
  - `id` (int)  
- Authentication: session required  

#### Delete Message
- Method: DELETE  
- URL: `/api/mailboxes/{name}/messages/{id}`  
- Path params: as above  
- Authentication: session required  

## 3. Response Details

- Standard success envelope for GET/POST:
  ```json
  { "data": { ... }, "meta": { ... } }
  ```
- Error envelope:
  ```json
  { "error": { "code": "STRING", "message": "human readable" } }
  ```

### Status Codes by Endpoint
- 200 OK: successful GET  
- 201 Created: successful POST (register, create key, generate mailbox)  
- 204 No Content: successful DELETE, logout  
- 400 Bad Request: validation errors  
- 401 Unauthorized: missing/invalid session or invitation key  
- 404 Not Found: mailbox/message/key not found  
- 409 Conflict: uniqueness violation (email, key, mailbox name)  
- 415 Unsupported Media Type: invalid message format  
- 500 Internal Server Error: unhandled exceptions  

## 4. Data Flow

1. **Registration**  
   • Validate DTO → InvitationKeyService.delete(key) + UserService.create(email, hash(password)) in one transaction → return user data.  
2. **Login/Logout**  
   • Validate DTO → AuthService.authenticate → Flask-Login.session_refresh → return message.  
3. **Mailbox operations**  
   • Validate name → MailboxService.get_or_create(name, user) → return mailbox metadata.  
   • Generate random: MailboxService.generate_random(user) → persist unique name.  
4. **Messaging**  
   • List: MessageService.query(mailbox.id, pagination, sort) → return list.  
   • View: MessageService.get(messageId) → strip `<script>` tags → return body & metadata.  
   • Delete: MessageService.delete(messageId) → 204.  

## 5. Security Considerations

- **Authentication**: cookie-based via Flask-Login, session timeout configured.  
- **Authorization**: every mailbox/message endpoint checks session and mailbox existence.  
- **CSRF**: implement tokens on all state-changing routes or use JWT with proper CORS.  
- **XSS**: sanitize message body by stripping `<script>` tags.  
- **Rate limiting**: apply Flask-Limiter to registration and login to mitigate brute-force.  

## 6. Error Handling

- All exceptions caught by centralized error handler → log via `app.logger` and return `500`.  
- Validation errors → Marshmallow `ValidationError` → 400 + error details.  
- Not found → custom `NotFoundError` → 404.  
- Duplicate → catch `IntegrityError` from SQLAlchemy → 409.  
- Unauthorized → handled by Flask-Login → 401.  

## 7. Performance

- **Indices**: ensure DB indexes on `invitation_keys(key)`, `users(email)`, `mailboxes(name)`, `messages(mailbox_id, received_at)`.  
- **Pagination**: limit pageSize, default 20, max 100.  
- **Query optimization**: eager-load related mailbox metadata if needed.  
- **Polling**: client polls list endpoint every 60 s—ensure efficient queries via index on `received_at`.  

## 8. Implementation Steps

1. Define Marshmallow schemas in `schemas/` (InvitationKeySchema, RegisterSchema, etc.).  
2. Create service classes in `services/` (InvitationKeyService, AuthService, MailboxService, MessageService).  
3. Register Blueprints:
   - `api/invitation_keys.py`  
   - `api/auth.py`  
   - `api/mailboxes.py`  
   - `api/messages.py`  
4. Implement routes using Flask-RESTful or plain Flask + decorators, injecting schemas and services.  
5. Configure Flask-Login in app factory; enforce `@login_required` on protected routes.  
6. Add Flask-Limiter rules for registration/login.  
7. Hook centralized error handler in app factory: catch custom and generic exceptions.  
8. Write unit tests for schemas, services, and integration tests for each endpoint.  
9. Update documentation with OpenAPI/Swagger definitions.  
10. Deploy and perform manual testing in Chrome, validate polling and error scenarios.  