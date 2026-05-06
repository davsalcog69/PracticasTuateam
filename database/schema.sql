-- PostgreSQL Database Schema for CocheExport Intelligence
-- Current as of 2026-05-06

-- Main table for raw car data from scrapers
CREATE TABLE IF NOT EXISTS cars (
    id VARCHAR(255) PRIMARY KEY, -- URL used as unique identifier
    portal TEXT,
    brand VARCHAR(100),
    model VARCHAR(100),
    year INTEGER,
    mileage INTEGER,
    kilometrage INTEGER,
    fuel TEXT,
    power INTEGER,
    price DOUBLE PRECISION,
    currency TEXT,
    country VARCHAR(100),
    location TEXT,
    url TEXT,
    source_url TEXT,
    images JSONB, -- Array of image URLs
    version TEXT,
    vehicle_status VARCHAR(100) NOT NULL DEFAULT 'Dudoso',
    vehicle_status_check VARCHAR(100) NOT NULL DEFAULT 'Dudoso'
);

-- Table for analyzed profitable opportunities
CREATE TABLE IF NOT EXISTS car_export (
    id TEXT PRIMARY KEY,
    portal TEXT,
    brand TEXT,
    model TEXT,
    year INTEGER,
    mileage INTEGER,
    fuel TEXT,
    power INTEGER,
    price DOUBLE PRECISION,
    currency TEXT,
    country TEXT,
    location TEXT,
    url TEXT,
    price_eur DOUBLE PRECISION,
    price_spain_avg DOUBLE PRECISION,
    transport_cost DOUBLE PRECISION,
    import_tax DOUBLE PRECISION,
    itv_cost DOUBLE PRECISION,
    registration_cost DOUBLE PRECISION,
    gestor_cost DOUBLE PRECISION,
    total_import_cost DOUBLE PRECISION,
    final_price DOUBLE PRECISION,
    estimated_profit DOUBLE PRECISION,
    roi_percentage DOUBLE PRECISION,
    images JSONB,
    source_url TEXT,
    vehicle_status VARCHAR(100) NOT NULL DEFAULT 'Dudoso',
    vehicle_status_check VARCHAR(100) NOT NULL DEFAULT 'Dudoso',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Users table (Integrated with Supabase Auth or standalone)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_admin BOOLEAN DEFAULT FALSE,
    avatar VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
