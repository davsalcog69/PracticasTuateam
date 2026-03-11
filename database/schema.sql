CREATE TABLE IF NOT EXISTS ads (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50),
    title TEXT,
    price DECIMAL(12, 2),
    year INT,
    kms INT,
    country_of_origin VARCHAR(50),
    url TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
