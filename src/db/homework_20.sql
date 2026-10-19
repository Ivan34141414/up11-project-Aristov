-- Создание справочников
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

-- Создание товаров
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(category_id),
    name VARCHAR(200) NOT NULL,
    manufacturer VARCHAR(100),
    price NUMERIC(10,2) CHECK (price > 0)
);

-- Создание остатков
CREATE TABLE stock_items (
    stock_item_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    variant_id INTEGER REFERENCES variants(variant_id),
    quantity INTEGER CHECK (quantity >= 0)
);

-- Создание пользователей
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    login VARCHAR(50) NOT NULL UNIQUE,
    role_id INTEGER REFERENCES roles(role_id)
);

-- Создание заказов и состава
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
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