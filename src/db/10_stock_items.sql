CREATE DATABASE stock_db;

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE sizes (
    size_id SERIAL PRIMARY KEY,
    value NUMERIC(4,1) NOT NULL UNIQUE
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(category_id),
    name VARCHAR(200) NOT NULL,
    price NUMERIC(10,2) CHECK (price > 0)
);

INSERT INTO categories (name) VALUES
('Наушники'),
('Колонки');

INSERT INTO sizes (value) VALUES
(1.0),
(2.0),
(3.0);

INSERT INTO products (category_id, name, price) VALUES
(1, 'Наушники Sony', 34990.00),
(2, 'Колонка JBL', 12990.00);

CREATE TABLE stock_items (
    stock_item_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    size_id INTEGER REFERENCES sizes(size_id),
    quantity INTEGER CHECK (quantity >= 0)
);

INSERT INTO stock_items (product_id, size_id, quantity) VALUES
(1, 1, 5),
(1, 2, 3),
(1, 3, 7),
(2, 1, 10),
(2, 2, 0);

INSERT INTO stock_items (product_id, size_id, quantity) VALUES (1, 1, -5);
INSERT INTO stock_items (product_id, size_id, quantity) VALUES (1, 1, 0);
INSERT INTO stock_items (product_id, size_id, quantity) VALUES (1, 1, 100);
INSERT INTO stock_items (product_id, size_id, quantity) VALUES (999, 1, 5);
INSERT INTO stock_items (product_id, size_id, quantity) VALUES (1, 999, 5);
INSERT INTO stock_items (product_id, size_id, quantity) VALUES (2, 3, 15);

DROP TABLE IF EXISTS stock_items CASCADE;

CREATE TABLE stock_items (
    stock_item_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    size_id INTEGER REFERENCES sizes(size_id),
    quantity INTEGER CHECK (quantity >= 0)
);

INSERT INTO stock_items (product_id, size_id, quantity) VALUES
(1, 1, 10),
(1, 2, 5),
(1, 3, 8),
(2, 1, 15),
(2, 2, 0);

INSERT INTO stock_items (product_id, size_id, quantity) VALUES (1, 1, -10);

DROP TABLE IF EXISTS stock_items CASCADE;

CREATE TABLE stock_items (
    stock_item_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER CHECK (quantity >= 0)
);

DROP TABLE IF EXISTS stock_items CASCADE;

CREATE TABLE stock_items (
    stock_item_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    size_id INTEGER REFERENCES sizes(size_id),
    quantity INTEGER CHECK (quantity >= 0)
);

DROP TABLE IF EXISTS stock_items CASCADE;

CREATE TABLE stock_items (
    stock_item_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    size_id INTEGER REFERENCES sizes(size_id),
    quantity INTEGER CHECK (quantity >= 0),
    reserved INTEGER CHECK (reserved >= 0)
);

DROP TABLE IF EXISTS stock_items CASCADE;

CREATE TABLE stock_items (
    stock_item_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    size_id INTEGER REFERENCES sizes(size_id),
    quantity INTEGER CHECK (quantity >= 0),
    reserved INTEGER CHECK (reserved >= 0)
);