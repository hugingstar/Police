CREATE DATABASE trade;

CREATE TABLE IF NOT EXISTS "nyse_log" (
                    Time_stamp TEXT,
                    Open TEXT,
                    High TEXT,
                    Low TEXT,
                    Close TEXT,
                    Volume TEXT,
                    Change TEXT,
                    Symbol TEXT,
                    Name TEXT
                );