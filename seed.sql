INSERT INTO employees (id, full_name, birth_date, salary, experience_years)
SELECT 1, 'Иванов Иван Иванович', '1985-04-12', 75000.50, 10
WHERE NOT EXISTS (SELECT 1 FROM employees WHERE id = 1);

INSERT INTO employees (id, full_name, birth_date, salary, experience_years)
SELECT 2, 'Петрова Анна Сергеевна', '1990-11-23', 82000.00, 7
WHERE NOT EXISTS (SELECT 1 FROM employees WHERE id = 2);

INSERT INTO employees (id, full_name, birth_date, salary, experience_years)
SELECT 3, 'Сидоров Пётр Васильевич', '1978-01-05', 95000.75, 15
WHERE NOT EXISTS (SELECT 1 FROM employees WHERE id = 3);

INSERT INTO projects (id, name, description, start_date, budget, manager_id)
SELECT 1, 'Внедрение CRM', 'Автоматизация отдела продаж и интеграция с 1С.', '2025-06-01', 1500000.00, 1
WHERE NOT EXISTS (SELECT 1 FROM projects WHERE id = 1);

INSERT INTO projects (id, name, description, start_date, budget, manager_id)
SELECT 2, 'Мобильное приложение', 'Разработка iOS и Android версии клиентского приложения.', '2025-09-15', 3000000.00, 2
WHERE NOT EXISTS (SELECT 1 FROM projects WHERE id = 2);

INSERT INTO projects (id, name, description, start_date, budget, manager_id)
SELECT 3, 'Обучение персонала', 'План развития soft skills для сотрудников.', '2025-03-10', 500000.00, 1
WHERE NOT EXISTS (SELECT 1 FROM projects WHERE id = 3);