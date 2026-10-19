# Отчет о проверке импорта (Пара 18)

**Тема проекта:** Мир аудиотехники
**СУБД:** PostgreSQL 18.6
**Дата проверки:** 17.10.2026

## 1. Выполненные SQL-запросы
Для проверки количества записей в базе данных были выполнены следующие запросы:

```sql
SELECT COUNT(*) FROM categories;
SELECT COUNT(*) FROM variants;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM stock_items;
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM order_items;