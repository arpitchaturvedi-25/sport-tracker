-- SportTracker database schema
-- This file is for reference — app.py creates these tables automatically
-- on first run via init_db().

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    age INTEGER,
    weight REAL,
    height REAL,
    daily_step_goal INTEGER DEFAULT 10000,
    daily_water_goal REAL DEFAULT 2.5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS running_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    run_date TEXT NOT NULL,
    start_time TEXT,
    end_time TEXT,
    duration_seconds INTEGER,
    distance_km REAL,
    avg_speed_kmh REAL,
    calories REAL,
    route_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS water_intake (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    log_date TEXT NOT NULL,
    amount_liters REAL NOT NULL,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS daily_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_date TEXT NOT NULL,
    steps INTEGER DEFAULT 0,
    distance_km REAL DEFAULT 0,
    calories REAL DEFAULT 0,
    running_time_seconds INTEGER DEFAULT 0,
    water_liters REAL DEFAULT 0,
    UNIQUE(user_id, activity_date),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
