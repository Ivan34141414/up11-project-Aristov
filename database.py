import psycopg2
from psycopg2 import pool

class Database:
    def __init__(self):
        self.connection_pool = None
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1, 5,
                host="localhost", port=5432, database="audio_db",
                user="postgres", password="123"
            )
        except Exception as e:
            print(f"Ошибка БД: {e}")
            self.connection_pool = None

    def get_connection(self):
        if self.connection_pool:
            return self.connection_pool.getconn()
        return None

    def release_connection(self, conn):
        if self.connection_pool and conn:
            self.connection_pool.putconn(conn)

    def close_all(self):
        if self.connection_pool:
            self.connection_pool.closeall()

    def get_categories(self):
        conn = self.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM categories ORDER BY name")
            categories = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return categories
        except psycopg2.Error as e:
            print(f"Ошибка запроса категорий: {e}")
            return []
        finally:
            self.release_connection(conn)

    def get_products(self, search_query="", category_name="Все категории", sort_order="По возрастанию"):
        conn = self.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            
            search_param = f"%{search_query}%"
            sort_dir = "ASC" if sort_order == "По возрастанию" else "DESC"
            
            query = f"""
                WITH order_counts AS (
                    SELECT oi.product_id, COUNT(*) as cnt
                    FROM order_items oi
                    JOIN orders o ON oi.order_id = o.order_id
                    WHERE o.order_date >= CURRENT_DATE - INTERVAL '1 month'
                    GROUP BY oi.product_id
                )
                SELECT 
                    p.product_id, 
                    p.name, 
                    c.name AS category_name, 
                    p.manufacturer, 
                    p.composition, 
                    p.price, 
                    p.image_path,
                    COALESCE(SUM(si.quantity), 0) AS total_quantity
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN stock_items si ON p.product_id = si.product_id
                LEFT JOIN order_counts oc ON p.product_id = oc.product_id
                WHERE (p.name ILIKE %s OR p.description ILIKE %s)
                AND (c.name = %s OR %s = 'Все категории')
                GROUP BY p.product_id, c.name, p.name, p.manufacturer, p.composition, p.price, p.image_path, oc.cnt
                ORDER BY 
                    CASE 
                        WHEN COALESCE(oc.cnt, 0) = 0 THEN p.price * 0.75 
                        ELSE p.price 
                    END {sort_dir};
            """
            
            cursor.execute(query, (search_param, search_param, category_name, category_name))
            products = cursor.fetchall()
            cursor.close()
            return products
        except psycopg2.Error as e:
            print(f"Ошибка запроса товаров: {e}")
            return []
        finally:
            self.release_connection(conn)

    def execute_query(self, sql, params=None):
        conn = self.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except psycopg2.Error as e:
            print(f"Ошибка запроса: {e}")
            return []
        finally:
            self.release_connection(conn)

    def execute_update(self, sql, params=None):
        conn = self.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            cursor.close()
            return True
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            print(f"Ошибка обновления: {e}")
            return False
        finally:
            self.release_connection(conn)