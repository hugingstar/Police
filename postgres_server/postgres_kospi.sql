CREATE DATABASE trade;

CREATE TABLE IF NOT EXISTS "kospi_log" (
                    Time_stamp TEXT,
                    Open TEXT,
                    High TEXT,
                    Low TEXT,
                    Close TEXT,
                    Volume TEXT,
                    Change TEXT,
                    Code TEXT,
                    Name TEXT
                );