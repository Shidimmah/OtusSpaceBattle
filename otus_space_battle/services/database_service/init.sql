CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS matches (
    id SERIAL PRIMARY KEY,
    player1_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    player2_id INTEGER NULL REFERENCES users(id) ON DELETE CASCADE,
    start_time TIMESTAMP DEFAULT NOW(),
    end_time TIMESTAMP NULL,
    winner_id INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'waiting',  -- waiting, in_progress, finished
    is_ranked BOOLEAN DEFAULT TRUE
);
