DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS player_attributes;
DROP TABLE IF EXISTS attributes;
DROP TABLE IF EXISTS pantheons;
DROP TABLE IF EXISTS technologies;
DROP TABLE IF EXISTS tech_bonuses;
DROP TABLE IF EXISTS tech_prerequisites;
DROP TABLE IF EXISTS system_variables;
DROP TABLE IF EXISTS player_technologies;

/* Old table names */
DROP TABLE IF EXISTS tech;

CREATE TABLE players (
    /* basic stats */
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255),
    display_name VARCHAR(255),
    discord_id VARCHAR(255),
    pantheon INTEGER DEFAULT -1
);

CREATE TABLE player_attributes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id INTEGER,
    attribute_id INTEGER,
    value FLOAT,
    start_turn INTEGER DEFAULT -1,
    expiry_turn INTEGER DEFAULT -1
);
CREATE TABLE player_technologies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id INTEGER,
    technology_id INTEGER
);
CREATE TABLE attributes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255),
    display_name VARCHAR(255)
);

CREATE TABLE pantheons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255),
    display_name VARCHAR(255)
);

CREATE TABLE technologies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255),
    display_name VARCHAR(255),
    description VARCHAR(255),
    cost INTEGER,
    chance_multiplier FLOAT DEFAULT 1
);

CREATE TABLE tech_bonuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tech_id INTEGER,
    attribute_id INTEGER,
    value FLOAT
);

CREATE TABLE tech_prerequisites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tech_id INTEGER,
    prerequisite_id INTEGER,
    is_hard BOOLEAN NOT NULL CHECK (is_hard IN (0, 1)) DEFAULT 1,
    cost_bonus INTEGER DEFAULT 0
);
CREATE TABLE system_variables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255),
    display_name VARCHAR(255),
    value VARCHAR(255)
)