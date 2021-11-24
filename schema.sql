DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS player_attributes;
DROP TABLE IF EXISTS attributes;
DROP TABLE IF EXISTS pantheons;
DROP TABLE IF EXISTS tech;
DROP TABLE IF EXISTS tech_bonuses;
DROP TABLE IF EXISTS system_variables;
CREATE TABLE players (
    /* basic stats */
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255),
    discord_id VARCHAR(255),
    pantheon INTEGER DEFAULT -1,
    tech JSON
    );

CREATE TABLE player_attributes(
    column_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER,
    attribute_id INTEGER,
    value FLOAT,
    start_turn INTEGER DEFAULT -1,
    expiry_turn INTEGER DEFAULT -1
    );

CREATE TABLE attributes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255)
    );

CREATE TABLE pantheons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255)
    );

CREATE TABLE tech (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255),
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
CREATE TABLE system_variables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255),
    value VARCHAR(255)
)