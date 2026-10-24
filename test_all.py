import psycopg2
from discount import calculate_price

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="audio_db",
    user="postgres",
    password="123"
)
cursor = conn.cursor()

cursor.execute("SELECT product_id, name, price FROM products;")

products = cursor.fetchall()

print(f"{'№':<3} | {'Товар':<25} | {'Цена':<8} | {'Итог':<8} | {'Скидка'}")
print("-" * 65)

for row in products:
    product_id = row[0]
    name = row[1]
    price = float(row[2])

    final_price = calculate_price(product_id, price)

    if final_price < price:
        discount = "Да"
    else:
        discount = "Нет"

    print(f"{product_id:<3} | {name[:25]:<25} | {price:<8} | {final_price:<8} | {discount}")

cursor.close()
conn.close()