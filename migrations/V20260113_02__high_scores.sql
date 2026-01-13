-- High scores table
CREATE TABLE IF NOT EXISTS high_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL,
    score INTEGER NOT NULL,
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for efficient top 10 queries
CREATE INDEX IF NOT EXISTS idx_high_scores_score ON high_scores(score DESC);
