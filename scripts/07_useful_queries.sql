-- ============================================
-- Файл: 07_useful_queries.sql
-- Назначение: полезные запросы для работы с базой данных
-- ============================================

-- ============================================
-- 1. ОТЧЁТЫ ПО ПЕРСОНАЛУ
-- ============================================

-- Список всех сотрудников с полной информацией
SELECT 
    e.personnel_number AS "Табельный номер",
    e.full_name AS "ФИО",
    d.name AS "Отдел",
    p.title AS "Должность",
    s.amount AS "Оклад",
    e.hire_date AS "Дата приёма",
    CASE 
        WHEN e.termination_date IS NULL THEN 'Работает'
        ELSE 'Уволен'
    END AS "Статус"
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
LEFT JOIN positions p ON e.position_id = p.position_id
LEFT JOIN LATERAL (
    SELECT amount 
    FROM salaries 
    WHERE employee_id = e.employee_id 
    ORDER BY effective_date DESC 
    LIMIT 1
) s ON true
WHERE e.termination_date IS NULL
ORDER BY d.name, p.title, e.full_name;

-- Структура компании (иерархия)
WITH RECURSIVE org_hierarchy AS (
    -- Топ-менеджеры (без руководителя)
    SELECT 
        employee_id,
        full_name,
        manager_id,
        1 AS level,
        full_name AS path
    FROM employees
    WHERE manager_id IS NULL AND termination_date IS NULL
    
    UNION ALL
    
    -- Подчинённые
    SELECT 
        e.employee_id,
        e.full_name,
        e.manager_id,
        oh.level + 1,
        oh.path || ' > ' || e.full_name
    FROM employees e
    INNER JOIN org_hierarchy oh ON e.manager_id = oh.employee_id
    WHERE e.termination_date IS NULL
)
SELECT 
    REPEAT('  ', level - 1) || full_name AS "Иерархия",
    level AS "Уровень"
FROM org_hierarchy
ORDER BY path;

-- Статистика по отделам
SELECT 
    d.name AS "Отдел",
    COUNT(e.employee_id) AS "Количество сотрудников",
    ROUND(AVG(s.amount), 2) AS "Средний оклад",
    MIN(s.amount) AS "Минимальный оклад",
    MAX(s.amount) AS "Максимальный оклад"
FROM departments d
LEFT JOIN employees e ON d.department_id = e.department_id AND e.termination_date IS NULL
LEFT JOIN LATERAL (
    SELECT amount 
    FROM salaries 
    WHERE employee_id = e.employee_id 
    ORDER BY effective_date DESC 
    LIMIT 1
) s ON true
GROUP BY d.name
ORDER BY COUNT(e.employee_id) DESC;

-- ============================================
-- 2. УЧЁТ РАБОЧЕГО ВРЕМЕНИ
-- ============================================

-- Отчёт по посещаемости за текущий месяц
SELECT 
    e.full_name AS "Сотрудник",
    COUNT(CASE WHEN a.status = 'present' THEN 1 END) AS "Присутствовал",
    COUNT(CASE WHEN a.status = 'absent' THEN 1 END) AS "Отсутствовал",
    COUNT(CASE WHEN a.status = 'vacation' THEN 1 END) AS "Отпуск",
    COUNT(CASE WHEN a.status = 'sick' THEN 1 END) AS "Больничный",
    COUNT(CASE WHEN a.status = 'remote' THEN 1 END) AS "Удалённо",
    ROUND(SUM(a.hours_worked), 2) AS "Всего часов"
FROM employees e
LEFT JOIN attendance a ON e.employee_id = a.employee_id 
    AND a.work_date >= DATE_TRUNC('month', CURRENT_DATE)
    AND a.work_date < DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'
WHERE e.termination_date IS NULL
GROUP BY e.employee_id, e.full_name
ORDER BY e.full_name;

-- Опоздания (приход после 9:15)
SELECT 
    e.full_name AS "Сотрудник",
    a.work_date AS "Дата",
    a.check_in AS "Время прихода",
    EXTRACT(EPOCH FROM (a.check_in::time - '09:15:00'::time)) / 60 AS "Опоздание (мин)"
FROM attendance a
JOIN employees e ON a.employee_id = e.employee_id
WHERE a.check_in::time > '09:15:00'
    AND a.work_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY a.work_date DESC, e.full_name;

-- ============================================
-- 3. ПРОЕКТЫ И ЗАДАЧИ
-- ============================================

-- Активные проекты с прогрессом
SELECT 
    p.name AS "Проект",
    e.full_name AS "Менеджер",
    p.start_date AS "Начало",
    p.end_date AS "Окончание",
    COUNT(t.task_id) AS "Всего задач",
    COUNT(CASE WHEN t.status = 'completed' THEN 1 END) AS "Завершено",
    ROUND(
        COUNT(CASE WHEN t.status = 'completed' THEN 1 END)::numeric / 
        NULLIF(COUNT(t.task_id), 0) * 100, 
        2
    ) AS "Прогресс (%)",
    p.budget AS "Бюджет",
    p.actual_cost AS "Затрачено"
FROM projects p
LEFT JOIN employees e ON p.manager_id = e.employee_id
LEFT JOIN tasks t ON p.project_id = t.project_id
WHERE p.status = 'active'
GROUP BY p.project_id, p.name, e.full_name, p.start_date, p.end_date, p.budget, p.actual_cost
ORDER BY p.start_date;

-- Просроченные задачи
SELECT 
    p.name AS "Проект",
    t.title AS "Задача",
    e.full_name AS "Исполнитель",
    t.deadline AS "Дедлайн",
    CURRENT_DATE - t.deadline AS "Просрочено (дней)",
    t.priority AS "Приоритет"
FROM tasks t
JOIN projects p ON t.project_id = p.project_id
LEFT JOIN employees e ON t.assigned_to = e.employee_id
WHERE t.deadline < CURRENT_DATE 
    AND t.status NOT IN ('completed', 'blocked')
ORDER BY t.priority DESC, t.deadline;

-- Загруженность сотрудников по задачам
SELECT 
    e.full_name AS "Сотрудник",
    COUNT(t.task_id) AS "Активных задач",
    SUM(t.estimated_hours) AS "Оценка часов",
    COUNT(CASE WHEN t.priority = 'critical' THEN 1 END) AS "Критичных",
    COUNT(CASE WHEN t.priority = 'high' THEN 1 END) AS "Высокий приоритет"
FROM employees e
LEFT JOIN tasks t ON e.employee_id = t.assigned_to 
    AND t.status IN ('new', 'in_progress')
WHERE e.termination_date IS NULL
GROUP BY e.employee_id, e.full_name
HAVING COUNT(t.task_id) > 0
ORDER BY COUNT(t.task_id) DESC;

-- ============================================
-- 4. ФИНАНСЫ
-- ============================================

-- Фонд оплаты труда по отделам
SELECT 
    d.name AS "Отдел",
    COUNT(e.employee_id) AS "Сотрудников",
    SUM(s.amount) AS "ФОТ (месяц)",
    SUM(s.amount) * 12 AS "ФОТ (год)",
    ROUND(AVG(s.amount), 2) AS "Средняя зарплата"
FROM departments d
LEFT JOIN employees e ON d.department_id = e.department_id AND e.termination_date IS NULL
LEFT JOIN LATERAL (
    SELECT amount 
    FROM salaries 
    WHERE employee_id = e.employee_id 
    ORDER BY effective_date DESC 
    LIMIT 1
) s ON true
GROUP BY d.name
ORDER BY SUM(s.amount) DESC;

-- Расчётный лист за последний период
SELECT 
    e.full_name AS "Сотрудник",
    p.period_start AS "Период с",
    p.period_end AS "Период по",
    p.base_salary AS "Оклад",
    p.bonus AS "Премия",
    p.deductions AS "Удержания",
    p.net_amount AS "К выплате"
FROM payroll p
JOIN employees e ON p.employee_id = e.employee_id
WHERE p.period_start = (SELECT MAX(period_start) FROM payroll)
ORDER BY e.full_name;

-- ============================================
-- 5. ОБОРУДОВАНИЕ
-- ============================================

-- Оборудование за сотрудниками
SELECT 
    e.full_name AS "Сотрудник",
    d.name AS "Отдел",
    a.name AS "Оборудование",
    a.type AS "Тип",
    a.serial_number AS "Серийный номер",
    aa.assigned_date AS "Дата выдачи",
    a.warranty_until AS "Гарантия до"
FROM asset_assignments aa
JOIN assets a ON aa.asset_id = a.asset_id
JOIN employees e ON aa.employee_id = e.employee_id
JOIN departments d ON e.department_id = d.department_id
WHERE aa.returned_date IS NULL
ORDER BY e.full_name, a.type;

-- Доступное оборудование
SELECT 
    a.name AS "Название",
    a.type AS "Тип",
    a.serial_number AS "Серийный номер",
    a.purchase_date AS "Дата покупки",
    a.warranty_until AS "Гарантия до",
    s.name AS "Поставщик"
FROM assets a
LEFT JOIN suppliers s ON a.supplier_id = s.supplier_id
WHERE a.status = 'available'
ORDER BY a.type, a.name;

-- Истекающие гарантии (в ближайшие 3 месяца)
SELECT 
    a.name AS "Оборудование",
    a.serial_number AS "Серийный номер",
    a.warranty_until AS "Гарантия до",
    a.warranty_until - CURRENT_DATE AS "Осталось дней",
    s.name AS "Поставщик",
    s.phone AS "Телефон"
FROM assets a
LEFT JOIN suppliers s ON a.supplier_id = s.supplier_id
WHERE a.warranty_until BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '3 months'
ORDER BY a.warranty_until;

-- ============================================
-- 6. ОБУЧЕНИЕ И РАЗВИТИЕ
-- ============================================

-- Матрица навыков отдела
SELECT 
    e.full_name AS "Сотрудник",
    s.name AS "Навык",
    es.level AS "Уровень (1-5)",
    CASE 
        WHEN es.level >= 4 THEN 'Эксперт'
        WHEN es.level = 3 THEN 'Опытный'
        WHEN es.level = 2 THEN 'Средний'
        ELSE 'Начальный'
    END AS "Оценка"
FROM employees e
JOIN employee_skills es ON e.employee_id = es.employee_id
JOIN skills s ON es.skill_id = s.skill_id
WHERE e.department_id = 2  -- Отдел разработки
ORDER BY s.name, es.level DESC;

-- Сертификаты с истекающим сроком
SELECT 
    e.full_name AS "Сотрудник",
    c.title AS "Курс",
    cert.issue_date AS "Дата получения",
    cert.expiry_date AS "Срок действия до",
    cert.expiry_date - CURRENT_DATE AS "Осталось дней"
FROM certificates cert
JOIN employees e ON cert.employee_id = e.employee_id
JOIN courses c ON cert.course_id = c.course_id
WHERE cert.expiry_date IS NOT NULL
    AND cert.expiry_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '6 months'
ORDER BY cert.expiry_date;

-- ============================================
-- 7. KPI И АНАЛИТИКА
-- ============================================

-- Результаты KPI за последний период
SELECT 
    e.full_name AS "Сотрудник",
    d.name AS "Отдел",
    ki.name AS "Показатель",
    ki.target_value AS "План",
    kr.actual_value AS "Факт",
    ROUND((kr.actual_value / NULLIF(ki.target_value, 0)) * 100, 2) AS "Выполнение (%)",
    kr.score AS "Баллы"
FROM employee_kpi_results kr
JOIN employees e ON kr.employee_id = e.employee_id
JOIN departments d ON e.department_id = d.department_id
JOIN kpi_indicators ki ON kr.indicator_id = ki.indicator_id
JOIN kpi_periods kp ON kr.period_id = kp.period_id
WHERE kp.is_active = true
ORDER BY e.full_name, ki.name;

-- Топ-10 сотрудников по KPI
SELECT 
    e.full_name AS "Сотрудник",
    d.name AS "Отдел",
    SUM(kr.score) AS "Общий балл",
    COUNT(kr.indicator_id) AS "Показателей"
FROM employee_kpi_results kr
JOIN employees e ON kr.employee_id = e.employee_id
JOIN departments d ON e.department_id = d.department_id
JOIN kpi_periods kp ON kr.period_id = kp.period_id
WHERE kp.is_active = true
GROUP BY e.employee_id, e.full_name, d.name
ORDER BY SUM(kr.score) DESC
LIMIT 10;

-- ============================================
-- 8. РЕКРУТИНГ
-- ============================================

-- Воронка найма
SELECT 
    c.status AS "Статус",
    COUNT(*) AS "Количество",
    ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM candidates) * 100, 2) AS "Процент"
FROM candidates c
GROUP BY c.status
ORDER BY 
    CASE c.status
        WHEN 'new' THEN 1
        WHEN 'contacted' THEN 2
        WHEN 'interviewed' THEN 3
        WHEN 'offered' THEN 4
        WHEN 'hired' THEN 5
        WHEN 'rejected' THEN 6
    END;

-- Кандидаты с собеседованиями
SELECT 
    c.full_name AS "Кандидат",
    p.title AS "Вакансия",
    i.interview_date AS "Дата собеседования",
    e.full_name AS "Интервьюер",
    i.rating AS "Оценка",
    i.status AS "Статус"
FROM candidates c
LEFT JOIN interviews i ON c.candidate_id = i.candidate_id
LEFT JOIN positions p ON c.position_applied = p.position_id
LEFT JOIN employees e ON i.employee_id = e.employee_id
WHERE c.status IN ('interviewed', 'offered')
ORDER BY i.interview_date DESC;

-- ============================================
-- 9. СЛУЖЕБНЫЕ ЗАПРОСЫ
-- ============================================

-- Размер таблиц
SELECT 
    schemaname AS "Схема",
    tablename AS "Таблица",
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS "Размер"
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Статистика по таблицам
SELECT 
    schemaname AS "Схема",
    tablename AS "Таблица",
    n_tup_ins AS "Вставок",
    n_tup_upd AS "Обновлений",
    n_tup_del AS "Удалений",
    n_live_tup AS "Живых строк",
    n_dead_tup AS "Мёртвых строк",
    last_vacuum AS "Последний VACUUM",
    last_analyze AS "Последний ANALYZE"
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_live_tup DESC;
