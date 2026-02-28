-- ============================================
-- Файл: 08_extensions.sql
-- Назначение: подключение полезных расширений PostgreSQL для SmartOffice
-- ============================================

-- ============================================
-- 1. БАЗОВЫЕ РАСШИРЕНИЯ (уже используются)
-- ============================================

-- Полнотекстовый поиск с триграммами
CREATE EXTENSION IF NOT EXISTS pg_trgm;
COMMENT ON EXTENSION pg_trgm IS 'Поиск по сходству строк, нечёткий поиск';

-- Исключающие ограничения для диапазонов
CREATE EXTENSION IF NOT EXISTS btree_gist;
COMMENT ON EXTENSION btree_gist IS 'Поддержка GiST индексов для обычных типов данных';

-- ============================================
-- 2. БЕЗОПАСНОСТЬ И ШИФРОВАНИЕ
-- ============================================

-- Криптографические функции
CREATE EXTENSION IF NOT EXISTS pgcrypto;
COMMENT ON EXTENSION pgcrypto IS 'Хеширование паролей, шифрование данных';

-- Пример использования pgcrypto:
-- Хеширование пароля: crypt('password', gen_salt('bf'))
-- Проверка пароля: password_hash = crypt('password', password_hash)
-- Шифрование: pgp_sym_encrypt('data', 'key')
-- Расшифровка: pgp_sym_decrypt(encrypted_data, 'key')

-- ============================================
-- 3. ГЕНЕРАЦИЯ UUID
-- ============================================

-- UUID для уникальных идентификаторов
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
COMMENT ON EXTENSION "uuid-ossp" IS 'Генерация UUID';

-- Пример использования:
-- SELECT uuid_generate_v4();
-- CREATE TABLE example (id UUID PRIMARY KEY DEFAULT uuid_generate_v4());

-- ============================================
-- 4. РАБОТА С ТЕКСТОМ
-- ============================================

-- Удаление диакритических знаков
CREATE EXTENSION IF NOT EXISTS unaccent;
COMMENT ON EXTENSION unaccent IS 'Удаление акцентов из текста';

-- Пример использования:
-- SELECT unaccent('café'); -- вернёт 'cafe'

-- Нечёткое сравнение строк
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
COMMENT ON EXTENSION fuzzystrmatch IS 'Расстояние Левенштейна, Soundex, Metaphone';

-- Примеры использования:
-- SELECT levenshtein('kitten', 'sitting'); -- расстояние редактирования
-- SELECT soundex('Smith'), soundex('Smyth'); -- поиск по звучанию
-- SELECT metaphone('PostgreSQL', 10);

-- ============================================
-- 5. РЕГИСТРОНЕЗАВИСИМЫЙ ТЕКСТ
-- ============================================

-- Тип данных citext для регистронезависимых строк
CREATE EXTENSION IF NOT EXISTS citext;
COMMENT ON EXTENSION citext IS 'Регистронезависимый тип текста';

-- Пример использования:
-- CREATE TABLE users (email citext UNIQUE);
-- SELECT * FROM users WHERE email = 'USER@EXAMPLE.COM'; -- найдёт user@example.com

-- ============================================
-- 6. ХРАНИЛИЩЕ КЛЮЧ-ЗНАЧЕНИЕ
-- ============================================

-- hstore для хранения пар ключ-значение
CREATE EXTENSION IF NOT EXISTS hstore;
COMMENT ON EXTENSION hstore IS 'Хранение пар ключ-значение';

-- Пример использования:
-- CREATE TABLE products (id SERIAL, attributes hstore);
-- INSERT INTO products (attributes) VALUES ('color => "red", size => "XL"');
-- SELECT * FROM products WHERE attributes->'color' = 'red';

-- ============================================
-- 7. ИЕРАРХИЧЕСКИЕ ДАННЫЕ
-- ============================================

-- ltree для работы с деревьями
CREATE EXTENSION IF NOT EXISTS ltree;
COMMENT ON EXTENSION ltree IS 'Иерархические структуры данных';

-- Пример использования:
-- CREATE TABLE categories (path ltree);
-- INSERT INTO categories VALUES ('electronics.computers.laptops');
-- SELECT * FROM categories WHERE path <@ 'electronics'; -- все подкатегории

-- ============================================
-- 8. СТАТИСТИКА И МОНИТОРИНГ
-- ============================================

-- Статистика выполнения запросов
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
COMMENT ON EXTENSION pg_stat_statements IS 'Сбор статистики по SQL-запросам';

-- Настройка в postgresql.conf:
-- shared_preload_libraries = 'pg_stat_statements'
-- pg_stat_statements.track = all

-- Примеры использования:
-- SELECT query, calls, total_exec_time, mean_exec_time 
-- FROM pg_stat_statements 
-- ORDER BY mean_exec_time DESC LIMIT 10;

-- ============================================
-- 9. ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ
-- ============================================

-- Дополнительные функции для работы с массивами, строками и т.д.
CREATE EXTENSION IF NOT EXISTS tablefunc;
COMMENT ON EXTENSION tablefunc IS 'Функции для работы с таблицами (crosstab, connectby)';

-- Пример crosstab (сводная таблица):
-- SELECT * FROM crosstab(
--   'SELECT department, month, revenue FROM sales ORDER BY 1,2',
--   'SELECT DISTINCT month FROM sales ORDER BY 1'
-- ) AS ct(department text, jan numeric, feb numeric, mar numeric);

-- ============================================
-- 10. ПОЛЕЗНЫЕ АДМИНИСТРАТИВНЫЕ РАСШИРЕНИЯ
-- ============================================

-- Информация о размере объектов БД
CREATE EXTENSION IF NOT EXISTS pgstattuple;
COMMENT ON EXTENSION pgstattuple IS 'Статистика по использованию места в таблицах';

-- Пример использования:
-- SELECT * FROM pgstattuple('employees');

-- ============================================
-- ПРОВЕРКА УСТАНОВЛЕННЫХ РАСШИРЕНИЙ
-- ============================================

-- Список всех установленных расширений
SELECT 
    extname AS "Расширение",
    extversion AS "Версия",
    extrelocatable AS "Перемещаемое",
    nspname AS "Схема"
FROM pg_extension e
JOIN pg_namespace n ON e.extnamespace = n.oid
ORDER BY extname;

-- ============================================
-- РЕКОМЕНДАЦИИ ПО ИСПОЛЬЗОВАНИЮ
-- ============================================

/*
1. pg_trgm - используйте для полнотекстового поиска по ФИО, названиям, описаниям
   CREATE INDEX idx_name_trgm ON table USING gin (name gin_trgm_ops);

2. pgcrypto - для безопасного хранения паролей и конфиденциальных данных
   password_hash = crypt('user_password', gen_salt('bf'))

3. uuid-ossp - для генерации уникальных идентификаторов в распределённых системах
   id UUID PRIMARY KEY DEFAULT uuid_generate_v4()

4. citext - для полей email, username, где регистр не важен
   email citext UNIQUE

5. hstore - для хранения дополнительных атрибутов без изменения схемы
   settings hstore

6. ltree - для категорий, организационных структур, файловых систем
   path ltree

7. pg_stat_statements - для мониторинга и оптимизации производительности
   Регулярно анализируйте медленные запросы

8. fuzzystrmatch - для поиска дубликатов, исправления опечаток
   WHERE levenshtein(name, 'search_term') < 3

9. unaccent - для нормализации текста при поиске
   WHERE unaccent(name) ILIKE unaccent('%search%')

10. btree_gist - для исключающих ограничений (непересекающиеся периоды)
    EXCLUDE USING gist (employee_id WITH =, period WITH &&)
*/

-- ============================================
-- ПРИМЕРЫ ПРИМЕНЕНИЯ В SMARTOFFICE
-- ============================================

-- Пример 1: Добавление поля с настройками пользователя (hstore)
-- ALTER TABLE employees ADD COLUMN preferences hstore;
-- UPDATE employees SET preferences = 'theme => "dark", language => "ru"' WHERE employee_id = 1;

-- Пример 2: Использование UUID для внешних интеграций
-- ALTER TABLE employees ADD COLUMN external_id UUID DEFAULT uuid_generate_v4();

-- Пример 3: Регистронезависимый email
-- ALTER TABLE employees ALTER COLUMN email TYPE citext;

-- Пример 4: Шифрование конфиденциальных данных
-- CREATE TABLE sensitive_data (
--     id SERIAL PRIMARY KEY,
--     employee_id INTEGER REFERENCES employees(employee_id),
--     encrypted_data BYTEA
-- );
-- INSERT INTO sensitive_data (employee_id, encrypted_data) 
-- VALUES (1, pgp_sym_encrypt('Конфиденциальная информация', 'secret_key'));

-- Пример 5: Поиск похожих имён (для дедупликации)
-- SELECT e1.full_name, e2.full_name, levenshtein(e1.full_name, e2.full_name) AS distance
-- FROM employees e1, employees e2
-- WHERE e1.employee_id < e2.employee_id
--   AND levenshtein(e1.full_name, e2.full_name) < 5
-- ORDER BY distance;
