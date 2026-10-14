CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    course INTEGER
);

INSERT INTO students (name, age, course) VALUES
('Иванов Иван', 18, 1),
('Петров Пётр', 19, 2),
('Сидорова Анна', 20, 3);

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    address TEXT
);

INSERT INTO clients (name, email, phone, address) VALUES
('Иванов Иван', 'ivanov@mail.ru', '+7-900-111-22-33', 'г. Москва, ул. Ленина, д. 1'),
('Петрова Анна', 'petrova@mail.ru', '+7-900-444-55-66', 'г. Санкт-Петербург, ул. Мира, д. 5'),
('Сидоров Пётр', 'sidorov@mail.ru', '+7-900-777-88-99', 'г. Казань, ул. Победы, д. 10');

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_date DATE DEFAULT CURRENT_DATE,
    delivery_date DATE,
    status VARCHAR(20) DEFAULT 'новый'
);

INSERT INTO orders (delivery_date, status) VALUES
('2026-10-20', 'в доставке'),
('2026-10-25', 'новый'),
('2026-10-15', 'доставлен');

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price NUMERIC(10,2) CHECK (price > 0),
    quantity INTEGER CHECK (quantity >= 0)
);

INSERT INTO products (name, price, quantity) VALUES
('Смартфон Samsung', 45000.50, 10),
('Ноутбук ASUS', 78000.00, 5),
('Наушники Sony', 12500.99, 25);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE
);

INSERT INTO users (login, is_active, is_admin) VALUES
('client1', TRUE, FALSE),
('manager1', TRUE, FALSE),
('admin1', TRUE, TRUE);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    year INTEGER CHECK (year > 1900),
    price NUMERIC(10,2) CHECK (price > 0),
    publish_date DATE,
    is_available BOOLEAN DEFAULT TRUE
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(100) NOT NULL,
    salary NUMERIC(10,2) CHECK (salary > 0),
    hire_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    views INTEGER DEFAULT 0,
    rating NUMERIC(3,1) CHECK (rating >= 0 AND rating <= 5),
    publish_date DATE,
    is_published BOOLEAN DEFAULT FALSE
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE DEFAULT CURRENT_DATE,
    amount NUMERIC(10,2) CHECK (amount > 0),
    is_paid BOOLEAN DEFAULT FALSE
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority INTEGER CHECK (priority BETWEEN 1 AND 5),
    due_date DATE,
    is_completed BOOLEAN DEFAULT FALSE
);

DROP TABLE IF EXISTS orders CASCADE;

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    registration_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date DATE DEFAULT CURRENT_DATE,
    total NUMERIC(10,2) CHECK (total >= 0),
    is_paid BOOLEAN DEFAULT FALSE
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_name VARCHAR(100) NOT NULL,
    quantity INTEGER CHECK (quantity > 0),
    price NUMERIC(10,2) CHECK (price > 0)
);

CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    birth_date DATE,
    country VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE books_shop (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author_id INTEGER REFERENCES authors(id),
    price NUMERIC(10,2) CHECK (price > 0),
    quantity INTEGER DEFAULT 0,
    publish_date DATE,
    is_available BOOLEAN DEFAULT TRUE
);

CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES books_shop(id),
    sale_date DATE DEFAULT CURRENT_DATE,
    total NUMERIC(10,2) CHECK (total >= 0),
    is_paid BOOLEAN DEFAULT FALSE
);