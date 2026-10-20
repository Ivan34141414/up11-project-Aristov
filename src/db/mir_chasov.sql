-- 1. Создание БД
CREATE DATABASE mir_chasov;

-- 2. Справочники
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO categories (name) VALUES 
('Наручные часы'), ('Настенные часы'), ('Настольные часы'), ('Детские часы');

CREATE TABLE sizes (
    size_id SERIAL PRIMARY KEY,
    value VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO sizes (value) VALUES 
('Чёрный'), ('Серебристый'), ('Золотистый');

-- 3. Товары
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(category_id),
    name VARCHAR(200) NOT NULL,
    price NUMERIC(10,2) CHECK (price > 0)
);

INSERT INTO products (category_id, name, price) VALUES 
(1, 'Наручные часы «Орион»', 2060),
(1, 'Наручные часы «Сириус»', 2630),
(1, 'Наручные часы «Вега»', 15540),
(1, 'Наручные часы «Атлас»', 3770),
(1, 'Наручные часы «Полюс»', 4340),
(1, 'Наручные часы «Горизонт»', 18090),
(1, 'Наручные часы «Ритм»', 5480),
(1, 'Наручные часы «Импульс»', 6050),
(1, 'Наручные часы «Такт»', 20640),
(1, 'Наручные часы «Эра»', 7190),
(1, 'Наручные часы «Контур»', 7760),
(1, 'Наручные часы «Спектр»', 23190),
(1, 'Наручные часы «Линия»', 8900),
(1, 'Наручные часы «Классик»', 9470),
(1, 'Наручные часы «Норд»', 25740),
(1, 'Наручные часы «Аврора»', 10610),
(1, 'Наручные часы «Компас»', 11180),
(1, 'Наручные часы «Фокус»', 28290),
(1, 'Наручные часы «Неон»', 12320),
(1, 'Наручные часы «Пульс»', 12890),
(2, 'Настенные часы «Луна»', 13460),
(2, 'Настенные часы «Солнце»', 14030),
(2, 'Настенные часы «Мозаика»', 14600),
(2, 'Настенные часы «Круг»', 15170),
(2, 'Настенные часы «Квадро»', 15740),
(2, 'Настенные часы «Лофт»', 16310),
(2, 'Настенные часы «Ретро»', 16880),
(3, 'Настольные часы «Мини»', 17450),
(3, 'Настольные часы «Луч»', 18020),
(4, 'Детские часы «Звезда»', 18590),
(4, 'Детские часы «Радуга»', 19160);

-- 4. Остатки
CREATE TABLE stock_items (
    stock_item_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    size_id INTEGER REFERENCES sizes(size_id),
    quantity INTEGER CHECK (quantity >= 0)
);

INSERT INTO stock_items (product_id, size_id, quantity) VALUES 
(1, 1, 8), (1, 2, 13), (1, 3, 18), (2, 1, 11), (2, 2, 16), (2, 3, 21),
(3, 1, 14), (3, 2, 19), (3, 3, 24), (4, 1, 17), (4, 2, 22), (4, 3, 27),
(5, 1, 20), (5, 2, 25), (5, 3, 6), (6, 1, 23), (6, 2, 28), (6, 3, 9),
(7, 1, 26), (7, 2, 7), (7, 3, 12), (8, 1, 5), (8, 2, 10), (8, 3, 15),
(9, 1, 8), (9, 2, 13), (9, 3, 18), (10, 1, 11), (10, 2, 16), (10, 3, 21),
(11, 1, 14), (11, 2, 19), (11, 3, 24), (12, 1, 17), (12, 2, 22), (12, 3, 27),
(13, 1, 20), (13, 2, 25), (13, 3, 6), (14, 1, 23), (14, 2, 28), (14, 3, 9),
(15, 1, 26), (15, 2, 7), (15, 3, 12), (16, 1, 5), (16, 2, 10), (16, 3, 15),
(17, 1, 8), (17, 2, 13), (17, 3, 18), (18, 1, 11), (18, 2, 16), (18, 3, 21),
(19, 1, 14), (19, 2, 19), (19, 3, 24), (20, 1, 17), (20, 2, 22), (20, 3, 27),
(21, 1, 20), (21, 2, 25), (21, 3, 6), (22, 1, 23), (22, 2, 28), (22, 3, 9),
(23, 1, 26), (23, 2, 7), (23, 3, 12), (24, 1, 5), (24, 2, 10), (24, 3, 15),
(25, 1, 8), (25, 2, 13), (25, 3, 18), (26, 1, 11), (26, 2, 16), (26, 3, 21),
(27, 1, 14), (27, 2, 19), (27, 3, 24), (28, 1, 2), (28, 2, 1), (28, 3, 1),
(29, 1, 1), (29, 2, 1), (29, 3, 1), (30, 1, 1), (30, 2, 0), (30, 3, 1),
(31, 1, 0), (31, 2, 0), (31, 3, 0);

-- 5. Пользователи
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO roles (name) VALUES 
('Администратор'), ('Менеджер'), ('Авторизованный пользователь');

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    login VARCHAR(50) NOT NULL UNIQUE,
    role_id INTEGER REFERENCES roles(role_id)
);

INSERT INTO users (last_name, first_name, middle_name, login, role_id) VALUES
('Иванов', 'Иван', 'Сергеевич', 'admin', 1),
('Петров', 'Пётр', 'Алексеевич', 'manager1', 2),
('Смирнова', 'Ольга', 'Викторовна', 'manager2', 2),
('Сидоров', 'Алексей', 'Иванович', 'client01', 3),
('Кузнецова', 'Анна', 'Ивановна', 'client02', 3),
('Орлов', 'Алексей', 'Иванович', 'client03', 3),
('Новикова', 'Анна', 'Ивановна', 'client04', 3),
('Морозов', 'Алексей', 'Иванович', 'client05', 3),
('Волкова', 'Анна', 'Ивановна', 'client06', 3),
('Соколов', 'Алексей', 'Иванович', 'client07', 3),
('Лебедева', 'Анна', 'Ивановна', 'client08', 3),
('Попов', 'Алексей', 'Иванович', 'client09', 3),
('Егорова', 'Анна', 'Ивановна', 'client10', 3),
('Зайцев', 'Алексей', 'Иванович', 'client11', 3),
('Павлова', 'Анна', 'Ивановна', 'client12', 3),
('Семёнов', 'Алексей', 'Иванович', 'client13', 3),
('Фёдорова', 'Анна', 'Ивановна', 'client14', 3),
('Козлов', 'Алексей', 'Иванович', 'client15', 3),
('Макарова', 'Анна', 'Ивановна', 'client16', 3),
('Белов', 'Алексей', 'Иванович', 'client17', 3);

-- 6. Заказы
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    user_id INTEGER REFERENCES users(user_id)
);

INSERT INTO orders (user_id) VALUES (4), (5), (6);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    size_id INTEGER REFERENCES sizes(size_id),
    quantity INTEGER CHECK (quantity > 0),
    price NUMERIC(10,2) CHECK (price > 0)
);

INSERT INTO order_items (order_id, product_id, size_id, quantity, price) VALUES
(1, 1, 1, 2, 2060),
(1, 2, 2, 1, 2630),
(2, 3, 3, 1, 15540);