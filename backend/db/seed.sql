PRAGMA foreign_keys = ON;

INSERT INTO users (username, password_hash, role, created_at)
VALUES ('admin', 'HASHED_PASSWORD_ADMIN', 'ADMIN', datetime('now'));

INSERT INTO users (username, password_hash, role, created_at)
VALUES ('user1', 'HASHED_PASSWORD_USER', 'USER', datetime('now'));
