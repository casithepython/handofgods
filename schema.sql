DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS player_attributes;
DROP TABLE IF EXISTS attributes;
DROP TABLE IF EXISTS pantheons;

CREATE TABLE players (
    /* basic stats */
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255),
    pantheon INTEGER DEFAULT -1,
    priests INTEGER DEFAULT 0,
    soldiers INTEGER DEFAULT 0,
    functionaries INTEGER DEFAULT 1000,
    power INTEGER DEFAULT 0,
    /* the following are just fun stats with no current in-game purpose */
    total_converted INTEGER DEFAULT 0,
    total_poached INTEGER DEFAULT 0,
    total_destroyed INTEGER DEFAULT 0,
    total_lost INTEGER DEFAULT 0,
    total_massacred INTEGER DEFAULT 0,
    total_population_lost INTEGER DEFAULT 0,
    total_spent INTEGER DEFAULT 0,
    total_income INTEGER DEFAULT 0
    );

CREATE TABLE player_attributes(
    column_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER,
    attribute_id INTEGER,
    value INTEGER,
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