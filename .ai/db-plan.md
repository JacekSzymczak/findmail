# PostgreSQL Database Schema Plan

1. Tables

## invitation_keys
```sql
CREATE TABLE invitation_keys (
    id SERIAL PRIMARY KEY,
    key VARCHAR(32) NOT NULL UNIQUE
);
```

## users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(254) NOT NULL UNIQUE,
    password VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

2. Relations
- No foreign key constraints (flat model).

3. Indices
```sql
CREATE UNIQUE INDEX ux_invitation_keys_key ON invitation_keys(key);
CREATE UNIQUE INDEX ux_users_email ON users(email);
```

4. PostgreSQL-specific settings
- Ensure database encoding is UTF8 with locale pl_PL.UTF-8 (LC_COLLATE, LC_CTYPE).
- Optionally use `TIMESTAMPTZ` instead of `TIMESTAMP` if timezone-aware timestamps are required.
- RLS not implemented (flat access model).

5. Additional notes
- Hash passwords with bcrypt or Argon2 at the application level before storage.
- Wrap invitation key deletion and user creation in a single transaction to maintain consistency:
  ```sql
  START TRANSACTION;
    DELETE FROM invitation_keys WHERE key = $1;
    INSERT INTO users (email, password, created_at) VALUES ($2, $3, CURRENT_TIMESTAMP);
  COMMIT;
  ```
- Plan for a password reset token mechanism in a future schema update (e.g., a `password_resets` table).
- Use a migration tool (e.g., Flyway, Alembic) to manage schema changes across environments. 