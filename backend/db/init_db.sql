-- =========================================
-- INIT DB - Système RAG (SQLite)
-- Windows / Local / Offline
-- =========================================

PRAGMA foreign_keys = ON;

-- ======================
-- Table : users
-- ======================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('ADMIN', 'USER')),
    created_at DATETIME NOT NULL
);

-- ======================
-- Table : documents
-- ======================
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL CHECK (file_type IN ('PDF', 'TXT', 'DOCX')),
    imported_at DATETIME NOT NULL
);

-- ======================
-- Table : chunks
-- ======================
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    vector_id TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id)
        ON DELETE CASCADE
);

-- ======================
-- Table : query_logs
-- ======================
CREATE TABLE IF NOT EXISTS query_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    used_documents TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ======================
-- Indexes (performance)
-- ======================
CREATE INDEX IF NOT EXISTS idx_chunks_document
    ON chunks(document_id);

CREATE INDEX IF NOT EXISTS idx_chunks_vector
    ON chunks(vector_id);

CREATE INDEX IF NOT EXISTS idx_logs_user
    ON query_logs(user_id);

CREATE INDEX IF NOT EXISTS idx_logs_date
    ON query_logs(created_at);
