-- 1. Создание БД
CREATE DATABASE audio_db;

-- 2. Очистка
DROP TABLE IF EXISTS order_items, orders, stock_items, users, roles, products, variants, categories CASCADE;

-- 3. Создание таблиц
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE variants (
    variant_id SERIAL PRIMARY KEY,
    value VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(category_id),
    name VARCHAR(200) NOT NULL,
    price NUMERIC(10,2) CHECK (price > 0)
);

CREATE TABLE stock_items (
    stock_item_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    variant_id INTEGER REFERENCES variants(variant_id),
    quantity INTEGER CHECK (quantity >= 0),
    price NUMERIC(10,2) CHECK (price > 0)
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    login VARCHAR(50) NOT NULL UNIQUE,
    role_id INTEGER REFERENCES roles(role_id)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE DEFAULT CURRENT_DATE,
    user_id INTEGER REFERENCES users(user_id)
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    variant_id INTEGER REFERENCES variants(variant_id),
    quantity INTEGER CHECK (quantity > 0),
    price NUMERIC(10,2) CHECK (price > 0)
);

-- 4. Заполнение справочников
INSERT INTO categories (name) VALUES 
('Наушники'), ('Колонки'), ('Акустические системы'), ('Микрофоны');

INSERT INTO variants (value) VALUES 
('Чёрный'), ('Белый'), ('Серебристый');

INSERT INTO roles (name) VALUES 
('Администратор'), ('Менеджер'), ('Клиент');

-- 5. Заполнение товаров (31 шт)
INSERT INTO products (category_id, name, price) VALUES 
(1, 'Наушники Sony WH-1000XM5', 34990.00),
(1, 'Наушники Sennheiser HD 660S', 42990.00),
(1, 'Наушники Apple AirPods Max', 59990.00),
(1, 'Наушники Bose QuietComfort 45', 31990.00),
(1, 'Наушники Marshall Major IV', 12990.00),
(2, 'Колонка JBL Charge 5', 12990.00),
(2, 'Колонка Bose SoundLink Flex', 18990.00),
(2, 'Колонка Sony SRS-XB33', 14990.00),
(2, 'Колонка Marshall Emberton', 16990.00),
(2, 'Колонка Xiaomi Mi Portable', 3990.00),
(3, 'Акустика Yamaha A-S301', 39990.00),
(3, 'Акустика Denon PMA-600NE', 45990.00),
(3, 'Акустика Pioneer A-10AE', 24990.00),
(3, 'Акустика Marantz PM6007', 54990.00),
(3, 'Акустика Onkyo TX-8220', 29990.00),
(4, 'Микрофон Sennheiser MK 4', 29990.00),
(4, 'Микрофон Audio-Technica AT2020', 10990.00),
(4, 'Микрофон Shure SM7B', 44990.00),
(4, 'Микрофон Rode NT1', 24990.00),
(4, 'Микрофон Behringer C-1', 5490.00),
(1, 'Наушники JBL Tune 510BT', 2990.00),
(1, 'Наушники Sennheiser Momentum 4', 37990.00),
(2, 'Колонка JBL Flip 6', 9990.00),
(2, 'Колонка Sony SRS-XG300', 25990.00),
(3, 'Акустика Yamaha R-S202', 24990.00),
(3, 'Акустика Denon RCD-M41', 42990.00),
(4, 'Микрофон Rode Wireless GO II', 32990.00),
(4, 'Микрофон Audio-Technica AT2035', 15990.00),
(1, 'Наушники Sony WF-1000XM4', 21990.00),
(2, 'Колонка Marshall Stanmore II', 34990.00),
(4, 'Микрофон Shure MV7', 29990.00);

-- 6. Заполнение пользователей (20 шт)
INSERT INTO users (last_name, first_name, login, role_id) VALUES
('Иванов', 'Иван', 'admin', 1),
('Петров', 'Пётр', 'manager1', 2),
('Смирнова', 'Ольга', 'manager2', 2),
('Сидоров', 'Алексей', 'client01', 3),
('Кузнецова', 'Анна', 'client02', 3),
('Орлов', 'Алексей', 'client03', 3),
('Новикова', 'Анна', 'client04', 3),
('Морозов', 'Алексей', 'client05', 3),
('Волкова', 'Анна', 'client06', 3),
('Соколов', 'Алексей', 'client07', 3),
('Лебедева', 'Анна', 'client08', 3),
('Попов', 'Алексей', 'client09', 3),
('Егорова', 'Анна', 'client10', 3),
('Зайцев', 'Алексей', 'client11', 3),
('Павлова', 'Анна', 'client12', 3),
('Семёнов', 'Алексей', 'client13', 3),
('Фёдорова', 'Анна', 'client14', 3),
('Козлов', 'Алексей', 'client15', 3),
('Макарова', 'Анна', 'client16', 3),
('Белов', 'Алексей', 'client17', 3);

-- 7. Заполнение остатков (93 шт)
INSERT INTO stock_items (product_id, variant_id, quantity, price) VALUES
(1, 1, 8, 10000), (1, 2, 13, 10000), (1, 3, 18, 10000),
(2, 1, 11, 10000), (2, 2, 16, 10000), (2, 3, 21, 10000),
(3, 1, 14, 10000), (3, 2, 19, 10000), (3, 3, 24, 10000),
(4, 1, 17, 10000), (4, 2, 22, 10000), (4, 3, 27, 10000),
(5, 1, 20, 10000), (5, 2, 25, 10000), (5, 3, 6, 10000),
(6, 1, 23, 10000), (6, 2, 28, 10000), (6, 3, 9, 10000),
(7, 1, 26, 10000), (7, 2, 7, 10000), (7, 3, 12, 10000),
(8, 1, 5, 10000), (8, 2, 10, 10000), (8, 3, 15, 10000),
(9, 1, 8, 10000), (9, 2, 13, 10000), (9, 3, 18, 10000),
(10, 1, 11, 10000), (10, 2, 16, 10000), (10, 3, 21, 10000),
(11, 1, 14, 10000), (11, 2, 19, 10000), (11, 3, 24, 10000),
(12, 1, 17, 10000), (12, 2, 22, 10000), (12, 3, 27, 10000),
(13, 1, 20, 10000), (13, 2, 25, 10000), (13, 3, 6, 10000),
(14, 1, 23, 10000), (14, 2, 28, 10000), (14, 3, 9, 10000),
(15, 1, 26, 10000), (15, 2, 7, 10000), (15, 3, 12, 10000),
(16, 1, 5, 10000), (16, 2, 10, 10000), (16, 3, 15, 10000),
(17, 1, 8, 10000), (17, 2, 13, 10000), (17, 3, 18, 10000),
(18, 1, 11, 10000), (18, 2, 16, 10000), (18, 3, 21, 10000),
(19, 1, 14, 10000), (19, 2, 19, 10000), (19, 3, 24, 10000),
(20, 1, 17, 10000), (20, 2, 22, 10000), (20, 3, 27, 10000),
(21, 1, 20, 10000), (21, 2, 25, 10000), (21, 3, 6, 10000),
(22, 1, 23, 10000), (22, 2, 28, 10000), (22, 3, 9, 10000),
(23, 1, 26, 10000), (23, 2, 7, 10000), (23, 3, 12, 10000),
(24, 1, 5, 10000), (24, 2, 10, 10000), (24, 3, 15, 10000),
(25, 1, 8, 10000), (25, 2, 13, 10000), (25, 3, 18, 10000),
(26, 1, 11, 10000), (26, 2, 16, 10000), (26, 3, 21, 10000),
(27, 1, 14, 10000), (27, 2, 19, 10000), (27, 3, 24, 10000),
(28, 1, 2, 10000), (28, 2, 1, 10000), (28, 3, 1, 10000),
(29, 1, 1, 10000), (29, 2, 1, 10000), (29, 3, 1, 10000),
(30, 1, 1, 10000), (30, 2, 0, 10000), (30, 3, 1, 10000),
(31, 1, 0, 10000), (31, 2, 0, 10000), (31, 3, 0, 10000);

-- 8. Заполнение заказов (15 шт)
INSERT INTO orders (order_date, user_id) VALUES
('2026-04-04', (SELECT user_id FROM users WHERE login='client01')),
('2026-04-06', (SELECT user_id FROM users WHERE login='client02')),
('2026-04-08', (SELECT user_id FROM users WHERE login='client03')),
('2026-04-10', (SELECT user_id FROM users WHERE login='client04')),
('2026-04-12', (SELECT user_id FROM users WHERE login='client05')),
('2026-04-14', (SELECT user_id FROM users WHERE login='client06')),
('2026-04-16', (SELECT user_id FROM users WHERE login='client07')),
('2026-04-18', (SELECT user_id FROM users WHERE login='client08')),
('2026-04-20', (SELECT user_id FROM users WHERE login='client09')),
('2026-04-22', (SELECT user_id FROM users WHERE login='client10')),
('2026-04-24', (SELECT user_id FROM users WHERE login='client11')),
('2026-04-26', (SELECT user_id FROM users WHERE login='client12')),
('2026-04-28', (SELECT user_id FROM users WHERE login='client13')),
('2026-04-30', (SELECT user_id FROM users WHERE login='client14')),
('2026-05-02', (SELECT user_id FROM users WHERE login='client15'));

-- 9. Заполнение состава заказов (30 шт)
INSERT INTO order_items (order_id, product_id, variant_id, quantity, price) VALUES
(1, (SELECT product_id FROM products WHERE name='Наушники Sony WH-1000XM5'), 1, 2, 1990.00),
(1, (SELECT product_id FROM products WHERE name='Колонка JBL Charge 5'), 2, 1, 2390.00),
(2, (SELECT product_id FROM products WHERE name='Наушники Sennheiser HD 660S'), 1, 1, 2790.00),
(2, (SELECT product_id FROM products WHERE name='Колонка Bose SoundLink Flex'), 2, 2, 3190.00),
(3, (SELECT product_id FROM products WHERE name='Наушники Apple AirPods Max'), 1, 2, 3490.00),
(3, (SELECT product_id FROM products WHERE name='Колонка Sony SRS-XB33'), 2, 1, 3890.00),
(4, (SELECT product_id FROM products WHERE name='Наушники Bose QuietComfort 45'), 1, 1, 4390.00),
(4, (SELECT product_id FROM products WHERE name='Колонка Marshall Emberton'), 2, 2, 4790.00),
(5, (SELECT product_id FROM products WHERE name='Наушники Marshall Major IV'), 1, 2, 2490.00),
(5, (SELECT product_id FROM products WHERE name='Колонка Xiaomi Mi Portable'), 2, 1, 2940.00),
(6, (SELECT product_id FROM products WHERE name='Акустика Yamaha A-S301'), 1, 1, 3390.00),
(6, (SELECT product_id FROM products WHERE name='Акустика Denon PMA-600NE'), 2, 2, 3840.00),
(7, (SELECT product_id FROM products WHERE name='Акустика Pioneer A-10AE'), 1, 2, 4290.00),
(7, (SELECT product_id FROM products WHERE name='Акустика Marantz PM6007'), 2, 1, 4740.00),
(8, (SELECT product_id FROM products WHERE name='Акустика Onkyo TX-8220'), 1, 1, 5190.00),
(8, (SELECT product_id FROM products WHERE name='Микрофон Sennheiser MK 4'), 2, 2, 1990.00),
(9, (SELECT product_id FROM products WHERE name='Микрофон Audio-Technica AT2020'), 1, 2, 2390.00),
(9, (SELECT product_id FROM products WHERE name='Микрофон Shure SM7B'), 2, 1, 2790.00),
(10, (SELECT product_id FROM products WHERE name='Микрофон Rode NT1'), 1, 1, 3190.00),
(10, (SELECT product_id FROM products WHERE name='Микрофон Behringer C-1'), 2, 2, 3490.00),
(11, (SELECT product_id FROM products WHERE name='Наушники JBL Tune 510BT'), 1, 2, 3890.00),
(11, (SELECT product_id FROM products WHERE name='Наушники Sennheiser Momentum 4'), 2, 1, 4390.00),
(12, (SELECT product_id FROM products WHERE name='Колонка JBL Flip 6'), 1, 1, 4790.00),
(12, (SELECT product_id FROM products WHERE name='Колонка Sony SRS-XG300'), 2, 2, 2490.00),
(13, (SELECT product_id FROM products WHERE name='Акустика Yamaha R-S202'), 1, 2, 2940.00),
(13, (SELECT product_id FROM products WHERE name='Акустика Denon RCD-M41'), 2, 1, 3390.00),
(14, (SELECT product_id FROM products WHERE name='Микрофон Rode Wireless GO II'), 1, 1, 3840.00),
(14, (SELECT product_id FROM products WHERE name='Микрофон Audio-Technica AT2035'), 2, 2, 4290.00),
(15, (SELECT product_id FROM products WHERE name='Наушники Sony WF-1000XM4'), 1, 2, 4740.00),
(15, (SELECT product_id FROM products WHERE name='Колонка Marshall Stanmore II'), 2, 1, 5190.00);