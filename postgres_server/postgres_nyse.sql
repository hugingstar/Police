CREATE TABLE IF NOT EXISTS "nyse_log" (
                    time_stamp TEXT,
                    open TEXT,
                    high TEXT,
                    low TEXT,
                    close TEXT,
                    volume TEXT,
                    change TEXT,
                    symbol TEXT,
                    name TEXT,
                    PRIMARY KEY (time_stamp, code)
                );