-- NaijaEdu CBT Database Schema
-- SQLite3

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ─── Users ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    UNIQUE NOT NULL,
    password_hash TEXT    NOT NULL,
    full_name     TEXT    NOT NULL,
    exam_number   TEXT    UNIQUE,
    email         TEXT,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login    TIMESTAMP
);

-- ─── Questions ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS questions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_type     TEXT NOT NULL CHECK(exam_type IN ('JAMB', 'WAEC')),
    subject       TEXT NOT NULL,
    year          INTEGER,
    question_text TEXT NOT NULL,
    option_a      TEXT,
    option_b      TEXT,
    option_c      TEXT,
    option_d      TEXT,
    option_e      TEXT,
    correct_option TEXT CHECK(correct_option IN ('A','B','C','D','E')),
    explanation   TEXT,
    image_path    TEXT,
    topic         TEXT,
    difficulty    TEXT CHECK(difficulty IN ('Easy','Medium','Hard'))
);

-- ─── Test Sessions ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS test_sessions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    exam_type           TEXT    NOT NULL,
    subject             TEXT    NOT NULL,
    start_time          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time            TIMESTAMP,
    score               INTEGER,
    total_questions     INTEGER DEFAULT 0,
    correct_answers     INTEGER DEFAULT 0,
    wrong_answers       INTEGER DEFAULT 0,
    skipped_questions   INTEGER DEFAULT 0,
    percentage_score    REAL    DEFAULT 0.0,
    time_spent_seconds  INTEGER DEFAULT 0,
    status              TEXT    DEFAULT 'In Progress'
                            CHECK(status IN ('In Progress','Completed','Abandoned')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── Answers ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS answers (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id          INTEGER NOT NULL,
    question_id         INTEGER NOT NULL,
    selected_option     TEXT,
    is_correct          BOOLEAN DEFAULT 0,
    time_spent_seconds  INTEGER DEFAULT 0,
    answered_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id)  REFERENCES test_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

-- ─── User Stats ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_stats (
    id                          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                     INTEGER UNIQUE NOT NULL,
    total_tests                 INTEGER DEFAULT 0,
    total_questions_answered    INTEGER DEFAULT 0,
    total_correct               INTEGER DEFAULT 0,
    total_wrong                 INTEGER DEFAULT 0,
    average_percentage          REAL    DEFAULT 0.0,
    best_subject                TEXT,
    last_test_date              TIMESTAMP,
    study_streak                INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── Indexes ──────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_questions_exam_subject ON questions(exam_type, subject);
CREATE INDEX IF NOT EXISTS idx_questions_year         ON questions(year);
CREATE INDEX IF NOT EXISTS idx_sessions_user          ON test_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status        ON test_sessions(status);
CREATE INDEX IF NOT EXISTS idx_answers_session        ON answers(session_id);
CREATE INDEX IF NOT EXISTS idx_answers_question       ON answers(question_id);
