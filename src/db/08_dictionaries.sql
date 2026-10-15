CREATE DATABASE dictionaries_db;

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    subcategory VARCHAR(100)
);

INSERT INTO categories (name, subcategory) VALUES
('Наручные', 'Классические'),
('Спортивные', 'Наручные'),
('Настенные', 'Интерьерные'),
('Ремешки', 'Аксессуары'),
('Браслеты', 'Аксессуары');

CREATE TABLE sizes (
    size_id SERIAL PRIMARY KEY,
    value NUMERIC(4,1) NOT NULL UNIQUE CHECK (value > 0)
);

INSERT INTO sizes (value) VALUES
(18), (19), (20), (21), (22), (23), (24), (25);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price NUMERIC(10,2) CHECK (price > 0),
    quantity INTEGER CHECK (quantity >= 0),
    category_id INTEGER REFERENCES categories(category_id)
);

INSERT INTO products (name, price, quantity, category_id) VALUES
('Часы наручные «Классика»', 15000.00, 10, 1),
('Часы наручные «Спорт»', 8500.50, 5, 2),
('Часы настенные «Интерьер»', 4200.00, 20, 3);

CREATE TABLE statuses (
    status_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO statuses (name) VALUES
('новый'),
('оплачен'),
('доставлен');

CREATE TABLE colors (
    color_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    code VARCHAR(7) CHECK (code LIKE '#%')
);

INSERT INTO colors (name, code) VALUES
('Чёрный', '#000000'),
('Белый', '#FFFFFF'),
('Серебристый', '#C0C0C0'),
('Синий', '#0000FF'),
('Красный', '#FF0000');

CREATE TABLE brands (
    brand_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    country VARCHAR(100) NOT NULL,
    founded_year INTEGER CHECK (founded_year > 1800 AND founded_year <= 2026)
);

CREATE TABLE units (
    unit_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    short_name VARCHAR(10) NOT NULL
);

INSERT INTO brands (name, country, founded_year) VALUES
('Sony', 'Япония', 1946),
('JBL', 'США', 1946),
('Bose', 'США', 1964),
('Sennheiser', 'Германия', 1945),
('Yamaha', 'Япония', 1887);

INSERT INTO units (name, short_name) VALUES
('Штука', 'шт'),
('Пара', 'пар'),
('Комплект', 'компл');

CREATE TABLE categories_audio (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

INSERT INTO categories_audio (name, description) VALUES
('Наушники', 'Проводные и беспроводные наушники'),
('Колонки', 'Портативные и стационарные колонки'),
('Акустические системы', 'Домашние и студийные акустические системы'),
('Микрофоны', 'Студийные и концертные микрофоны'),
('Аксессуары', 'Кабели, чехлы, стойки');

CREATE TABLE variants (
    variant_id SERIAL PRIMARY KEY,
    value VARCHAR(50) NOT NULL UNIQUE,
    code VARCHAR(7) CHECK (code LIKE '#%')
);

INSERT INTO variants (value, code) VALUES
('Чёрный', '#000000'),
('Белый', '#FFFFFF'),
('Серебристый', '#C0C0C0'),
('Синий', '#0000FF'),
('Красный', '#FF0000');

CREATE TABLE order_statuses (
    status_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    is_final BOOLEAN DEFAULT FALSE
);

INSERT INTO order_statuses (name, is_final) VALUES
('новый', FALSE),
('оплачен', FALSE),
('в доставке', FALSE),
('доставлен', TRUE),
('отменён', TRUE);