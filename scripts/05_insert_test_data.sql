-- Вставляем должности (если их нет)
INSERT INTO positions (title, min_salary, max_salary) VALUES
    ('Генеральный директор', 300000, 600000),
    ('Технический директор', 250000, 500000),
    ('Руководитель отдела разработки', 200000, 400000),
    ('Ведущий разработчик', 150000, 300000),
    ('Разработчик', 80000, 200000),
    ('Менеджер по продажам', 50000, 200000),
    ('Бухгалтер', 60000, 150000),
    ('HR-менеджер', 50000, 150000),
    ('Системный администратор', 70000, 180000)
ON CONFLICT (title) DO NOTHING;

-- Вставляем графики работы (если их нет)
INSERT INTO work_schedules (name, description, monday, tuesday, wednesday, thursday, friday, saturday, sunday, start_time, end_time) VALUES
    ('5/2 (9-18)', 'Стандартная пятидневка', true, true, true, true, true, false, false, '09:00', '18:00'),
    ('5/2 (10-19)', 'Пятидневка со смещением', true, true, true, true, true, false, false, '10:00', '19:00'),
    ('2/2 (9-21)', 'Сменный график 2 через 2', true, true, false, false, true, true, false, '09:00', '21:00')
ON CONFLICT (name) DO NOTHING;

-- Вставляем отделы (если их нет)
INSERT INTO departments (name) VALUES 
    ('Администрация'),
    ('Разработка'),
    ('Продажи'),
    ('Бухгалтерия'),
    ('HR')
ON CONFLICT (name) DO NOTHING;

-- Отключаем триггер
ALTER TABLE employees DISABLE TRIGGER generate_personnel_number_trigger;

-- Вставляем сотрудников с полными данными
INSERT INTO employees (full_name, birth_date, phone, email, hire_date, department_id, position_id, schedule_id) VALUES
    ('Александров Александр Александрович', '1985-03-15', '+7 (495) 111-11-11', 'a.alexandrov@smartoffice.ru', '2018-02-10', 1, 1, 1),
    ('Борисов Борис Борисович', '1982-07-22', '+7 (495) 222-22-22', 'b.borisov@smartoffice.ru', '2019-05-15', 2, 2, 1),
    ('Викторова Виктория Викторовна', '1988-11-30', '+7 (495) 333-33-33', 'v.viktorova@smartoffice.ru', '2020-03-20', 2, 3, 1),
    ('Григорьев Григорий Григорьевич', '1990-01-12', '+7 (495) 444-44-44', 'g.grigoriev@smartoffice.ru', '2021-07-01', 2, 4, 2),
    ('Дмитриева Дарья Дмитриевна', '1995-05-18', '+7 (495) 555-55-55', 'd.dmitrieva@smartoffice.ru', '2021-09-12', 2, 5, 2),
    ('Евгеньев Евгений Евгеньевич', '1987-09-25', '+7 (495) 666-66-66', 'e.evgenev@smartoffice.ru', '2022-01-17', 3, 6, 1),
    ('Жукова Жанна Жановна', '1983-12-08', '+7 (495) 777-77-77', 'j.zhukova@smartoffice.ru', '2020-11-22', 4, 7, 1),
    ('Зайцев Захар Захарович', '1992-04-14', '+7 (495) 888-88-88', 'z.zaytsev@smartoffice.ru', '2023-04-05', 5, 8, 1),
    ('Ильина Ирина Ильинична', '1996-08-20', '+7 (495) 999-99-99', 'i.ilina@smartoffice.ru', '2022-08-30', 2, 5, 2),
    ('Козлов Кирилл Кириллович', '1994-02-28', '+7 (495) 000-00-00', 'k.kozlov@smartoffice.ru', '2023-01-09', 2, 5, 2);

-- Включаем триггер обратно
ALTER TABLE employees ENABLE TRIGGER generate_personnel_number_trigger;

-- Генерируем табельные номера для всех сотрудников
UPDATE employees SET personnel_number = 'EMP' || LPAD(employee_id::text, 5, '0') WHERE personnel_number IS NULL;

-- Обновляем руководителей отделов (используем правильные ID)
UPDATE departments SET manager_id = 1 WHERE department_id = 1;
UPDATE departments SET manager_id = 2 WHERE department_id = 2;
UPDATE departments SET manager_id = 6 WHERE department_id = 3;
UPDATE departments SET manager_id = 7 WHERE department_id = 4;
UPDATE departments SET manager_id = 8 WHERE department_id = 5;

-- Обновляем руководителей сотрудников
UPDATE employees SET manager_id = 1 WHERE employee_id IN (2,6,7,8);
UPDATE employees SET manager_id = 2 WHERE employee_id IN (3,4,5,9,10);
UPDATE employees SET manager_id = 3 WHERE employee_id IN (4,9);

-- Адреса сотрудников
INSERT INTO employee_addresses (employee_id, address_type, city, street, house, apartment, postal_code, valid_from) VALUES
    (1, 'residential', 'Москва', 'ул. Тверская', '10', '25', '125009', '2018-02-10'),
    (2, 'residential', 'Москва', 'ул. Арбат', '15', '42', '119019', '2019-05-15'),
    (3, 'residential', 'Москва', 'ул. Ленина', '20', '18', '101000', '2020-03-20'),
    (4, 'residential', 'Москва', 'пр-т Мира', '35', '67', '129090', '2021-07-01'),
    (5, 'residential', 'Москва', 'ул. Пушкина', '8', '12', '109012', '2021-09-12'),
    (6, 'residential', 'Москва', 'ул. Чехова', '22', '5', '125047', '2022-01-17'),
    (7, 'residential', 'Москва', 'ул. Гоголя', '17', '33', '119034', '2020-11-22'),
    (8, 'residential', 'Москва', 'ул. Толстого', '12', '8', '119021', '2023-04-05'),
    (9, 'residential', 'Москва', 'ул. Достоевского', '9', '45', '101999', '2022-08-30'),
    (10, 'residential', 'Москва', 'ул. Маяковского', '25', '71', '125009', '2023-01-09');

-- Члены семьи
INSERT INTO family_members (employee_id, full_name, relationship, birth_date, is_dependent) VALUES
    (1, 'Александрова Анна Петровна', 'spouse', '1987-06-20', false),
    (1, 'Александров Алексей Александрович', 'child', '2015-09-10', true),
    (2, 'Борисова Вера Ивановна', 'spouse', '1984-03-15', false),
    (3, 'Викторов Владимир Сергеевич', 'spouse', '1986-08-22', false),
    (3, 'Викторова Валерия Владимировна', 'child', '2018-05-12', true),
    (5, 'Дмитриев Денис Олегович', 'spouse', '1993-11-30', false),
    (7, 'Жуков Жорж Жанович', 'spouse', '1981-07-18', false),
    (7, 'Жукова Жанна Жоржевна', 'child', '2012-02-28', true);

-- Банковские реквизиты
INSERT INTO employee_bank_details (employee_id, bank_name, bik, account_number, correspondent_account, is_default) VALUES
    (1, 'Сбербанк', '044525225', '40817810100000000001', '30101810400000000225', true),
    (2, 'ВТБ', '044525187', '40817810200000000002', '30101810700000000187', true),
    (3, 'Альфа-Банк', '044525593', '40817810300000000003', '30101810200000000593', true),
    (4, 'Тинькофф', '044525974', '40817810400000000004', '30101810145250000974', true),
    (5, 'Сбербанк', '044525225', '40817810500000000005', '30101810400000000225', true),
    (6, 'ВТБ', '044525187', '40817810600000000006', '30101810700000000187', true),
    (7, 'Газпромбанк', '044525823', '40817810700000000007', '30101810200000000823', true),
    (8, 'Райффайзенбанк', '044525700', '40817810800000000008', '30101810200000000700', true),
    (9, 'Сбербанк', '044525225', '40817810900000000009', '30101810400000000225', true),
    (10, 'Альфа-Банк', '044525593', '40817811000000000010', '30101810200000000593', true);

-- Зарплаты
INSERT INTO salaries (employee_id, effective_date, amount) VALUES
    (1, '2018-02-10', 450000),
    (2, '2019-05-15', 350000),
    (3, '2020-03-20', 280000),
    (4, '2021-07-01', 200000),
    (5, '2021-09-12', 120000),
    (6, '2022-01-17', 100000),
    (7, '2020-11-22', 90000),
    (8, '2023-04-05', 85000),
    (9, '2022-08-30', 110000),
    (10, '2023-01-09', 115000);

-- Поставщики
INSERT INTO suppliers (name, contact_person, phone, email, address) VALUES
    ('ООО "ТехноМир"', 'Петров Петр Петрович', '+7 (495) 123-45-67', 'info@technomir.ru', 'Москва, ул. Промышленная, 5'),
    ('АО "КомпьютерСервис"', 'Сидорова Светлана Сергеевна', '+7 (495) 234-56-78', 'sales@compserv.ru', 'Москва, пр-т Ленинский, 45'),
    ('ИП Иванов И.И.', 'Иванов Иван Иванович', '+7 (495) 345-67-89', 'ivanov@mail.ru', 'Москва, ул. Садовая, 12');

-- Оборудование
INSERT INTO assets (name, type, serial_number, supplier_id, purchase_date, purchase_price, warranty_until, status) VALUES
    ('Ноутбук Dell Latitude 5520', 'laptop', 'DL5520-001', 1, '2023-01-15', 85000, '2026-01-15', 'assigned'),
    ('Ноутбук HP ProBook 450', 'laptop', 'HP450-002', 1, '2023-02-20', 75000, '2026-02-20', 'assigned'),
    ('Монитор Dell 27"', 'monitor', 'DLM27-003', 2, '2023-01-15', 25000, '2026-01-15', 'assigned'),
    ('Монитор LG 24"', 'monitor', 'LG24-004', 2, '2023-03-10', 18000, '2026-03-10', 'assigned'),
    ('iPhone 14 Pro', 'phone', 'IP14P-005', 3, '2023-04-01', 95000, '2024-04-01', 'assigned'),
    ('Samsung Galaxy S23', 'phone', 'SGS23-006', 3, '2023-05-15', 75000, '2024-05-15', 'assigned'),
    ('Клавиатура Logitech', 'keyboard', 'LGK-007', 2, '2023-01-20', 3500, '2024-01-20', 'available'),
    ('Мышь Logitech MX Master', 'mouse', 'LGMX-008', 2, '2023-01-20', 7500, '2024-01-20', 'available');

-- Закрепление оборудования
INSERT INTO asset_assignments (asset_id, employee_id, assigned_date) VALUES
    (1, 1, '2023-01-16'),
    (2, 2, '2023-02-21'),
    (3, 3, '2023-01-16'),
    (4, 4, '2023-03-11'),
    (5, 1, '2023-04-02'),
    (6, 2, '2023-05-16');

-- Навыки
INSERT INTO skills (name, category) VALUES
    ('Python', 'Программирование'),
    ('JavaScript', 'Программирование'),
    ('SQL', 'Базы данных'),
    ('PostgreSQL', 'Базы данных'),
    ('React', 'Frontend'),
    ('Node.js', 'Backend'),
    ('Docker', 'DevOps'),
    ('Kubernetes', 'DevOps'),
    ('Управление проектами', 'Менеджмент'),
    ('Продажи', 'Бизнес');

-- Навыки сотрудников
INSERT INTO employee_skills (employee_id, skill_id, level) VALUES
    (2, 1, 5), (2, 3, 5), (2, 4, 5), (2, 7, 4),
    (3, 1, 4), (3, 3, 4), (3, 6, 4), (3, 9, 3),
    (4, 1, 4), (4, 2, 4), (4, 5, 4), (4, 6, 3),
    (5, 2, 3), (5, 5, 3), (5, 6, 2),
    (6, 10, 4),
    (9, 2, 3), (9, 5, 3),
    (10, 1, 2), (10, 3, 2);

-- Курсы
INSERT INTO courses (title, provider, duration_hours, description) VALUES
    ('Продвинутый Python', 'Coursera', 40, 'Углубленное изучение Python'),
    ('React для профессионалов', 'Udemy', 30, 'Продвинутая разработка на React'),
    ('Kubernetes Administration', 'Linux Foundation', 60, 'Администрирование Kubernetes'),
    ('Управление проектами Agile', 'PMI', 24, 'Agile методологии управления проектами'),
    ('PostgreSQL Performance Tuning', 'PostgreSQL.org', 16, 'Оптимизация производительности PostgreSQL');

-- Сертификаты
INSERT INTO certificates (employee_id, course_id, issue_date, grade) VALUES
    (2, 1, '2022-06-15', 'Отлично'),
    (2, 5, '2023-03-20', 'Отлично'),
    (3, 1, '2021-09-10', 'Хорошо'),
    (3, 4, '2022-11-25', 'Отлично'),
    (4, 2, '2023-01-15', 'Отлично'),
    (5, 2, '2023-05-20', 'Хорошо');

-- Проекты
INSERT INTO projects (name, description, start_date, end_date, status, manager_id, budget, actual_cost) VALUES
    ('Разработка CRM системы', 'Создание внутренней CRM для управления клиентами', '2023-01-10', '2023-12-31', 'active', 3, 5000000, 2800000),
    ('Миграция на облако', 'Перенос инфраструктуры в облако AWS', '2023-03-01', '2023-09-30', 'active', 2, 3000000, 1500000),
    ('Мобильное приложение', 'Разработка мобильного приложения для клиентов', '2023-06-01', '2024-03-31', 'active', 3, 4000000, 800000);

-- Команды проектов
INSERT INTO project_team (project_id, employee_id, role, joined_date) VALUES
    (1, 3, 'Руководитель проекта', '2023-01-10'),
    (1, 4, 'Ведущий разработчик', '2023-01-10'),
    (1, 5, 'Разработчик', '2023-01-15'),
    (1, 9, 'Разработчик', '2023-02-01'),
    (2, 2, 'Технический директор', '2023-03-01'),
    (2, 4, 'Ведущий разработчик', '2023-03-01'),
    (2, 10, 'Разработчик', '2023-03-15'),
    (3, 3, 'Руководитель проекта', '2023-06-01'),
    (3, 5, 'Разработчик', '2023-06-01'),
    (3, 9, 'Разработчик', '2023-06-01');

-- Задачи
INSERT INTO tasks (project_id, title, description, assigned_to, deadline, priority, estimated_hours, status) VALUES
    (1, 'Проектирование базы данных', 'Разработка схемы БД для CRM', 4, '2023-02-15', 'high', 40, 'completed'),
    (1, 'Разработка API', 'Создание REST API для CRM', 4, '2023-04-30', 'high', 120, 'in_progress'),
    (1, 'Разработка интерфейса', 'Создание пользовательского интерфейса', 5, '2023-06-30', 'medium', 160, 'in_progress'),
    (2, 'Анализ текущей инфраструктуры', 'Аудит существующей инфраструктуры', 2, '2023-03-31', 'critical', 80, 'completed'),
    (2, 'Настройка AWS', 'Конфигурация облачной инфраструктуры', 4, '2023-06-30', 'high', 100, 'in_progress'),
    (3, 'Дизайн мобильного приложения', 'Создание UI/UX дизайна', 5, '2023-07-31', 'high', 60, 'new');

-- Учет рабочего времени
INSERT INTO attendance (employee_id, work_date, check_in, check_out, status) VALUES
    (1, '2024-03-01', '2024-03-01 09:00:00', '2024-03-01 18:00:00', 'present'),
    (1, '2024-03-04', '2024-03-04 09:15:00', '2024-03-04 18:30:00', 'present'),
    (2, '2024-03-01', '2024-03-01 09:00:00', '2024-03-01 18:00:00', 'present'),
    (2, '2024-03-04', '2024-03-04 09:00:00', '2024-03-04 18:00:00', 'present'),
    (3, '2024-03-01', '2024-03-01 10:00:00', '2024-03-01 19:00:00', 'present'),
    (4, '2024-03-01', '2024-03-01 10:00:00', '2024-03-01 19:00:00', 'present'),
    (5, '2024-03-01', '2024-03-01 10:00:00', '2024-03-01 19:00:00', 'present'),
    (6, '2024-03-01', '2024-03-01 09:00:00', '2024-03-01 18:00:00', 'present'),
    (7, '2024-03-01', '2024-03-01 09:00:00', '2024-03-01 18:00:00', 'present'),
    (8, '2024-03-01', '2024-03-01 09:00:00', '2024-03-01 18:00:00', 'present');

-- Заявки на отпуск
INSERT INTO leave_requests (employee_id, start_date, end_date, leave_type, status, approved_by) VALUES
    (5, '2024-07-01', '2024-07-14', 'vacation', 'approved', 3),
    (9, '2024-08-15', '2024-08-28', 'vacation', 'approved', 3),
    (10, '2024-09-01', '2024-09-07', 'vacation', 'pending', NULL),
    (4, '2024-06-10', '2024-06-17', 'vacation', 'approved', 2);

-- Кандидаты
INSERT INTO candidates (full_name, birth_date, phone, email, position_applied, status, source, resume_text) VALUES
    ('Смирнов Сергей Сергеевич', '1993-05-20', '+7 (495) 111-22-33', 's.smirnov@example.com', 5, 'interviewed', 'hh.ru', 'Опыт разработки на Python 3 года'),
    ('Новикова Наталья Николаевна', '1991-08-15', '+7 (495) 222-33-44', 'n.novikova@example.com', 5, 'new', 'LinkedIn', 'Frontend разработчик, React, Vue.js'),
    ('Морозов Михаил Михайлович', '1989-12-10', '+7 (495) 333-44-55', 'm.morozov@example.com', 6, 'contacted', 'Рекомендация', 'Опыт в продажах B2B 5 лет');

-- Собеседования
INSERT INTO interviews (candidate_id, employee_id, interview_date, feedback, rating, status) VALUES
    (1, 3, '2024-02-15 14:00:00', 'Хорошие технические навыки, коммуникабелен', 8, 'completed'),
    (1, 4, '2024-02-20 15:00:00', 'Отличное знание Python, рекомендую к найму', 9, 'completed'),
    (3, 6, '2024-03-01 11:00:00', 'Опытный продавец, хорошо презентует себя', 7, 'completed');

-- Периоды KPI
INSERT INTO kpi_periods (name, start_date, end_date, is_active) VALUES
    ('Q1 2024', '2024-01-01', '2024-03-31', true),
    ('Q2 2024', '2024-04-01', '2024-06-30', false),
    ('Q3 2024', '2024-07-01', '2024-09-30', false),
    ('Q4 2024', '2024-10-01', '2024-12-31', false);

-- Показатели KPI
INSERT INTO kpi_indicators (name, description, unit, target_value, weight) VALUES
    ('Выполнение плана продаж', 'Процент выполнения плана продаж', '%', 100, 40),
    ('Удовлетворенность клиентов', 'Средний балл удовлетворенности', 'балл', 4.5, 30),
    ('Количество закрытых задач', 'Количество выполненных задач в срок', 'шт', 20, 30);

-- Результаты KPI
INSERT INTO employee_kpi_results (employee_id, period_id, indicator_id, actual_value, score) VALUES
    (6, 1, 1, 105, 42),
    (6, 1, 2, 4.7, 31),
    (4, 1, 3, 22, 33),
    (5, 1, 3, 18, 27);

-- Командировки
INSERT INTO business_trips (employee_id, destination, start_date, end_date, purpose, status) VALUES
    (2, 'Санкт-Петербург', '2024-04-10', '2024-04-12', 'Встреча с партнерами', 'planned'),
    (6, 'Казань', '2024-05-15', '2024-05-17', 'Презентация продукта', 'planned'),
    (3, 'Екатеринбург', '2024-02-20', '2024-02-22', 'Конференция по разработке', 'completed');

-- Документы
INSERT INTO documents (file_name, file_path, mime_type, document_type) VALUES
    ('passport_alexandrov.pdf', '/docs/passports/alexandrov.pdf', 'application/pdf', 'passport'),
    ('diploma_borisov.pdf', '/docs/diplomas/borisov.pdf', 'application/pdf', 'diploma'),
    ('contract_viktorova.pdf', '/docs/contracts/viktorova.pdf', 'application/pdf', 'contract');

-- Связь документов с сотрудниками
INSERT INTO employee_documents (employee_id, document_id) VALUES
    (1, 1),
    (2, 2),
    (3, 3);

-- Расчетные листы
INSERT INTO payroll (employee_id, period_start, period_end, base_salary, bonus, deductions, payment_date) VALUES
    (1, '2024-02-01', '2024-02-29', 450000, 50000, 65000, '2024-03-05'),
    (2, '2024-02-01', '2024-02-29', 350000, 30000, 49400, '2024-03-05'),
    (3, '2024-02-01', '2024-02-29', 280000, 20000, 39000, '2024-03-05'),
    (4, '2024-02-01', '2024-02-29', 200000, 15000, 27950, '2024-03-05'),
    (5, '2024-02-01', '2024-02-29', 120000, 10000, 16900, '2024-03-05'),
    (6, '2024-02-01', '2024-02-29', 100000, 25000, 16250, '2024-03-05'),
    (7, '2024-02-01', '2024-02-29', 90000, 5000, 12350, '2024-03-05'),
    (8, '2024-02-01', '2024-02-29', 85000, 5000, 11700, '2024-03-05'),
    (9, '2024-02-01', '2024-02-29', 110000, 8000, 15340, '2024-03-05'),
    (10, '2024-02-01', '2024-02-29', 115000, 10000, 16250, '2024-03-05');
