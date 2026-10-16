CREATE DATABASE products_db;

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO categories (name) VALUES
('Наручные'),
('Настенные'),
('Аксессуары');

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(category_id),
    name VARCHAR(200) NOT NULL,
    manufacturer VARCHAR(100),
    description TEXT,
    composition TEXT,
    price NUMERIC(10,2) CHECK (price > 0),
    image_path VARCHAR(255)
);

INSERT INTO products (category_id, name, manufacturer, description, composition, price, image_path) VALUES
(1, 'Часы наручные «Классика»', 'Восток', 'Механические часы', 'Сталь, кожа', 15000.00, 'watch_1.png'),
(2, 'Часы наручные «Спорт»', 'Casio', 'Электронные часы', 'Пластик, резина', 5000.00, 'watch_2.png'),
(3, 'Часы настенные «Интерьер»', 'Янтарь', 'Кварцевые часы', 'Дерево, стекло', 4200.00, 'watch_3.png'),
(1, 'Часы наручные «Премиум»', 'Rolex', 'Люксовые часы', 'Золото, сталь', 850000.00, 'watch_4.png'),
(3, 'Браслет кожаный', 'Ремешок', 'Аксессуар для часов', 'Кожа', 1500.00, 'watch_5.png');

INSERT INTO products (category_id, name, manufacturer, price) VALUES (1, 'Брак', 'Тест', -100);
INSERT INTO products (category_id, name, manufacturer, price) VALUES (1, 'Бесплатный', 'Тест', 0);
INSERT INTO products (category_id, name, manufacturer, price) VALUES (1, 'Часы «Тест»', 'Тест', 100);
INSERT INTO products (category_id, name, manufacturer, price) VALUES (999, 'Товар', 'Тест', 1000);
INSERT INTO products (category_id, name, manufacturer, price) VALUES (2, 'Часы «Корректные»', 'Casio', 3000);

DROP TABLE products CASCADE;

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price NUMERIC(10,2) CHECK (price > 0),
    image_path VARCHAR(255)
);

DROP TABLE products CASCADE;

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(category_id),
    name VARCHAR(200) NOT NULL,
    manufacturer VARCHAR(100),
    price NUMERIC(10,2) CHECK (price > 0),
    image_path VARCHAR(255)
);

DROP TABLE products CASCADE;

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(category_id),
    name VARCHAR(200) NOT NULL,
    manufacturer VARCHAR(100),
    description TEXT,
    composition TEXT,
    price NUMERIC(10,2) CHECK (price > 0),
    quantity INTEGER CHECK (quantity >= 0),
    image_path VARCHAR(255)
);

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

CREATE TABLE products_audio (
    product_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories_audio(category_id),
    name VARCHAR(200) NOT NULL,
    manufacturer VARCHAR(100),
    description TEXT,
    composition TEXT,
    price NUMERIC(10,2) CHECK (price > 0),
    image_path VARCHAR(255)
);

INSERT INTO products_audio (category_id, name, manufacturer, description, composition, price, image_path) VALUES
(1, 'Наушники WH-1000XM5', 'Sony', 'Беспроводные с шумоподавлением', 'Пластик, кожа', 34990.00, 'headphones_1.png'),
(1, 'Наушники HD 660S', 'Sennheiser', 'Открытые студийные', 'Металл, пластик', 42990.00, 'headphones_2.png'),
(2, 'Колонка Charge 5', 'JBL', 'Портативная Bluetooth', 'Пластик, резина', 12990.00, 'speaker_1.png'),
(2, 'Колонка SoundLink Flex', 'Bose', 'Защита IP67', 'Силикон', 18990.00, 'speaker_2.png'),
(4, 'Микрофон MK 4', 'Sennheiser', 'Студийный конденсаторный', 'Металл', 29990.00, 'mic_1.png');