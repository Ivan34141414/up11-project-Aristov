import psycopg2

def calculate_price_audio(item_id, base_price):
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="audio_db",
            user="postgres",
            password="123"
        )
        cursor = conn.cursor()
        
        query = """
            SELECT COUNT(*) 
            FROM order_items oi 
            JOIN orders o ON oi.order_id = o.order_id 
            WHERE oi.product_id = %s 
            AND o.order_date >= CURRENT_DATE - INTERVAL '1 month';
        """
        cursor.execute(query, (item_id,))
        result = cursor.fetchone()
        orders_count = result[0]
        
        cursor.close()
        conn.close()
        
        if orders_count == 0:
            return float(base_price) * 0.75
        else:
            return float(base_price)
            
    except psycopg2.Error as e:
        print(f"Ошибка БД: {e}")
        return None

# Тестовый запуск
if __name__ == "__main__":
    final_price = calculate_price_audio(1, 34990)
    print(f"Итоговая цена для товара 1: {final_price}")