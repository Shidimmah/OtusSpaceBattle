-- Battle Mechanics Service Tables
CREATE TABLE ships (
    id VARCHAR(36) PRIMARY KEY,
    position_x FLOAT NOT NULL,
    position_y FLOAT NOT NULL,
    direction_angle FLOAT NOT NULL,
    speed FLOAT NOT NULL,
    rotation_speed FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Resource Management Service Tables
CREATE TABLE ship_resources (
    ship_id VARCHAR(36) PRIMARY KEY REFERENCES ships(id),
    fuel FLOAT NOT NULL CHECK (fuel >= 0),
    torpedoes INTEGER NOT NULL CHECK (torpedoes >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Ranking Service Tables
CREATE TABLE player_rankings (
    player_id VARCHAR(36) PRIMARY KEY,
    rank_points INTEGER NOT NULL DEFAULT 0 CHECK (rank_points >= 0),
    games_played INTEGER NOT NULL DEFAULT 0,
    wins INTEGER NOT NULL DEFAULT 0,
    losses INTEGER NOT NULL DEFAULT 0,
    draws INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Analytics Service Tables
CREATE TABLE game_events (
    id SERIAL PRIMARY KEY,
    game_id VARCHAR(36) NOT NULL,
    player_id VARCHAR(36) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE game_statistics (
    game_id VARCHAR(36) PRIMARY KEY,
    duration FLOAT NOT NULL,
    shots_fired INTEGER NOT NULL DEFAULT 0,
    hits INTEGER NOT NULL DEFAULT 0,
    fuel_used FLOAT NOT NULL DEFAULT 0,
    winner_id VARCHAR(36),
    is_draw BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE player_statistics (
    player_id VARCHAR(36) PRIMARY KEY,
    total_games INTEGER NOT NULL DEFAULT 0,
    total_wins INTEGER NOT NULL DEFAULT 0,
    total_losses INTEGER NOT NULL DEFAULT 0,
    total_draws INTEGER NOT NULL DEFAULT 0,
    average_game_duration FLOAT NOT NULL DEFAULT 0,
    accuracy FLOAT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации запросов
CREATE INDEX idx_game_events_game_id ON game_events(game_id);
CREATE INDEX idx_game_events_player_id ON game_events(player_id);
CREATE INDEX idx_game_events_timestamp ON game_events(timestamp);
CREATE INDEX idx_player_rankings_rank_points ON player_rankings(rank_points DESC);

-- Триггеры для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_ships_updated_at
    BEFORE UPDATE ON ships
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ship_resources_updated_at
    BEFORE UPDATE ON ship_resources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_player_rankings_updated_at
    BEFORE UPDATE ON player_rankings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_game_statistics_updated_at
    BEFORE UPDATE ON game_statistics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 