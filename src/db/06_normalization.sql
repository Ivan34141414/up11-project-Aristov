CREATE DATABASE normalization_db;

-- ЗАДАНИЕ 2: 1НФ
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL
);

INSERT INTO users (name, phone) VALUES
('Иванов', '123-45-67'),
('Иванов', '890-12-34'),
('Петров', '555-55-55');

-- ЗАДАНИЕ 3: 2НФ
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    order_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL
);

CREATE TABLE order_items (
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER CHECK (quantity > 0),
    PRIMARY KEY (order_id, product_id)
);

INSERT INTO orders (order_id) VALUES (1), (2);

INSERT INTO products (product_id, product_name) VALUES
(10, 'Часы'),
(20, 'Браслет');

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(1, 10, 2),
(1, 20, 1),
(2, 10, 1);

-- ЗАДАНИЕ 4.1: 3НФ
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;

CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category_id INTEGER REFERENCES categories(category_id)
);

INSERT INTO categories (category_id, category_name) VALUES
(10, 'Наручные'),
(20, 'Аксессуары'),
(30, 'Настенные');

INSERT INTO products (name, category_id) VALUES
('Часы', 10),
('Браслет', 20),
('Будильник', 30);

-- ЗАДАНИЕ 4.2: 3НФ
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS manufacturers CASCADE;

CREATE TABLE manufacturers (
    manufacturer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    manufacturer_id INTEGER REFERENCES manufacturers(manufacturer_id)
);

INSERT INTO manufacturers (name, country) VALUES
('Восток', 'Россия'),
('Casio', 'Япония');

INSERT INTO products (name, manufacturer_id) VALUES
('Часы', 1),
('Браслет', 2),
('Будильник', 1);

-- ЗАДАНИЕ 5: Самостоятельная работа

DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS manufacturers CASCADE;
DROP TABLE IF EXISTS clients CASCADE;

CREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    client_name VARCHAR(100) NOT NULL,
    client_phone VARCHAR(20)
);

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE manufacturers (
    manufacturer_id SERIAL PRIMARY KEY,
    manufacturer_name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category_id INTEGER REFERENCES categories(category_id),
    manufacturer_id INTEGER REFERENCES manufacturers(manufacturer_id),
    price NUMERIC(10,2) CHECK (price > 0)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE DEFAULT CURRENT_DATE,
    client_id INTEGER REFERENCES clients(client_id)
);

CREATE TABLE order_items (
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER CHECK (quantity > 0),
    PRIMARY KEY (order_id, product_id)
);

INSERT INTO clients (client_name, client_phone) VALUES
('Сидорова', '123-45-67'),
('Павлова', '555-55-55');

INSERT INTO categories (category_name) VALUES
('Детская'),
('Женская');

INSERT INTO manufacturers (manufacturer_name, country) VALUES
('Восток', 'Россия'),
('Casio', 'Япония');

INSERT INTO products (product_name, category_id, manufacturer_id, price) VALUES
('Кроссовки', 1, 1, 2190),
('Сандалии', 1, 2, 2790),
('Сапоги', 2, 1, 2500);

INSERT INTO orders (order_date, client_id) VALUES
('2026-04-02', 1),
('2026-04-05', 2);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(1, 1, 1),
(1, 2, 1),
(2, 3, 1);

-- ЗАДАНИЕ 6, уровень 1 (базовый)
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

INSERT INTO users (name) VALUES
('Иванов'),
('Петров');


-- ЗАДАНИЕ 6, уровень 2 (средний)

DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category_id INTEGER REFERENCES categories(category_id)
);

CREATE TABLE order_items (
    order_id INTEGER,
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER CHECK (quantity > 0),
    PRIMARY KEY (order_id, product_id)
);

INSERT INTO categories (category_name) VALUES
('Наручные'),
('Аксессуары');

INSERT INTO products (product_name, category_id) VALUES
('Часы', 1),
('Браслет', 2);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(1, 1, 2),
(1, 2, 1),
(2, 1, 1);


-- ЗАДАНИЕ 6, уровень 3 (повышенный)

DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS manufacturers CASCADE;
DROP TABLE IF EXISTS clients CASCADE;

CREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    client_name VARCHAR(100) NOT NULL,
    client_email VARCHAR(100),
    client_phone VARCHAR(20)
);

CREATE TABLE manufacturers (
    manufacturer_id SERIAL PRIMARY KEY,
    manufacturer_name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    manufacturer_id INTEGER REFERENCES manufacturers(manufacturer_id),
    price NUMERIC(10,2) CHECK (price > 0)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE DEFAULT CURRENT_DATE,
    client_id INTEGER REFERENCES clients(client_id)
);

CREATE TABLE order_items (
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER CHECK (quantity > 0),
    PRIMARY KEY (order_id, product_id)
);

INSERT INTO clients (client_name, client_email, client_phone) VALUES
('Сидорова', 'sidorova@mail.ru', '123-45-67'),
('Павлова', 'pavlova@mail.ru', '555-55-55');

INSERT INTO manufacturers (manufacturer_name, country) VALUES
('Восток', 'Россия'),
('Casio', 'Япония');

INSERT INTO products (product_name, manufacturer_id, price) VALUES
('Кроссовки', 1, 2190),
('Сандалии', 2, 2790),
('Сапоги', 1, 2500);

INSERT INTO orders (order_date, client_id) VALUES
('2026-04-02', 1),
('2026-04-05', 2);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(1, 1, 1),
(1, 2, 1),
(2, 3, 1);

-- ЗАДАНИЕ 7: Творческий уровень (Мир аудиотехники)
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS manufacturers CASCADE;
DROP TABLE IF EXISTS clients CASCADE;

CREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    client_name VARCHAR(100) NOT NULL,
    client_phone VARCHAR(20)
);

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE manufacturers (
    manufacturer_id SERIAL PRIMARY KEY,
    manufacturer_name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category_id INTEGER REFERENCES categories(category_id),
    manufacturer_id INTEGER REFERENCES manufacturers(manufacturer_id),
    price NUMERIC(10,2) CHECK (price > 0)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE DEFAULT CURRENT_DATE,
    client_id INTEGER REFERENCES clients(client_id)
);

CREATE TABLE order_items (
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER CHECK (quantity > 0),
    PRIMARY KEY (order_id, product_id)
);

INSERT INTO clients (client_name, client_phone) VALUES
('Иванов', '111-22-33'),
('Петрова', '444-55-66');

INSERT INTO categories (category_name) VALUES
('Наушники'),
('Колонки');

INSERT INTO manufacturers (manufacturer_name, country) VALUES
('Sony', 'Япония'),
('JBL', 'США');

INSERT INTO products (product_name, category_id, manufacturer_id, price) VALUES
('Наушники WH-1000XM5', 1, 1, 34990),
('Колонка Charge 5', 2, 2, 12990);

INSERT INTO orders (client_id) VALUES
(1), (2);

INSERT INTO order_items (order_id, product_id, quantity) VALUES
(1, 1, 1),
(1, 2, 1),
(2, 1, 1);