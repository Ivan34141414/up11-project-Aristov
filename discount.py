import psycopg2

def calculate_price(product_id, base_price):
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="audio_db",
            user="postgres",
            password="123"
        )
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM products WHERE product_id = %s;", (product_id,))
        name_result = cursor.fetchone()
        product_name = name_result[0] if name_result else "Товар не найден"
        
        query = """
            SELECT COUNT(*) 
            FROM order_items oi 
            JOIN orders o ON oi.order_id = o.order_id 
            WHERE oi.product_id = %s 
            AND o.order_date >= CURRENT_DATE - INTERVAL '1 month';
        """
        cursor.execute(query, (product_id,))
        orders_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()

        base_price = float(base_price)
        
        if orders_count == 0:
            discount_size = base_price * 0.25
            final_price = base_price * 0.75
        else:
            discount_size = 0.0
            final_price = base_price

        print(f"Товар: {product_name} | Скидка: {discount_size} руб. | Итог: {final_price} руб.")

        return (final_price, discount_size)
        
    except psycopg2.Error as e:
        print(f"Ошибка БД: {e}")
        return (None, None)

# Тестовый запуск
if __name__ == "__main__":
    result = calculate_price(1, 34990)
    print("Результат работы функции (кортеж):", result)