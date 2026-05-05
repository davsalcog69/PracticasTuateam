-- Database Schema for Car Import AI

-- Table to track each scraping execution
CREATE TABLE IF NOT EXISTS scrape_runs (
    id SERIAL PRIMARY KEY,
    portal VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'running', -- 'running', 'completed', 'failed'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    items_scraped INTEGER DEFAULT 0
);

-- Main table for car ads
CREATE TABLE IF NOT EXISTS cars (
    id SERIAL PRIMARY KEY,
    scrape_run_id INTEGER REFERENCES scrape_runs(id),
    portal VARCHAR(50) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    version VARCHAR(255),
    year INTEGER,
    kilometrage INTEGER,
    fuel VARCHAR(50),
    transmission VARCHAR(50),
    power INTEGER,
    price DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'EUR',
    location VARCHAR(255),
    url TEXT UNIQUE NOT NULL, -- Used to avoid duplicates
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for car images (multiple images per car)
CREATE TABLE IF NOT EXISTS car_images (
    id SERIAL PRIMARY KEY,
    car_id INTEGER REFERENCES cars(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    order_index INTEGER DEFAULT 0
);

-- Table for user inspection requests
CREATE TABLE IF NOT EXISTS inspection_requests (
    id SERIAL PRIMARY KEY,
    car_id INTEGER REFERENCES cars(id) ON DELETE CASCADE,
    user_contact VARCHAR(255) NOT NULL, -- Email or phone
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'contacted', 'completed'
    notes TEXT
);
