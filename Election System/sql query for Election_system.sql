-- Set Up MySQL Database and Table:
-- First, you need to create a database and a table to store the election results. Below is the SQL script for setting this up.

CREATE DATABASE election_db;

USE election_db;

CREATE TABLE candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    votes INT DEFAULT 0
);

Add some candidates to the table:
INSERT INTO candidates (name) VALUES ('Alice');
INSERT INTO candidates (name) VALUES ('Bob');
INSERT INTO candidates (name) VALUES ('Charlie');
