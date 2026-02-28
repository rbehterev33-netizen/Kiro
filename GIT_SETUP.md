# 🚀 Инструкция по отправке проекта в GitHub

## Шаг 1: Установка Git

### Windows

1. Скачайте Git с официального сайта:
   https://git-scm.com/download/win

2. Запустите установщик и следуйте инструкциям
   - Оставьте настройки по умолчанию
   - Выберите "Use Git from the Windows Command Prompt"

3. После установки перезапустите терминал

4. Проверьте установку:
```cmd
git --version
```

### Альтернативный способ (через winget)

```powershell
winget install --id Git.Git -e --source winget
```

## Шаг 2: Настройка Git

Настройте ваше имя и email (они будут видны в коммитах):

```bash
git config --global user.name "Ваше Имя"
git config --global user.email "your.email@example.com"
```

## Шаг 3: Инициализация репозитория

Откройте терминал в папке SmartOffice и выполните:

```bash
# Перейдите в папку проекта
cd C:\Users\1\Documents\Kiro\SmartOffice

# Инициализируйте Git репозиторий
git init

# Добавьте все файлы
git add .

# Создайте первый коммит
git commit -m "Initial commit: SmartOffice v1.0.0"
```

## Шаг 4: Подключение к GitHub

```bash
# Добавьте удалённый репозиторий
git remote add origin https://github.com/rbehterev33-netizen/Kiro.git

# Переименуйте ветку в main (если нужно)
git branch -M main

# Отправьте изменения в GitHub
git push -u origin main
```

## Шаг 5: Проверка

Откройте ваш репозиторий на GitHub:
https://github.com/rbehterev33-netizen/Kiro

Вы должны увидеть все файлы проекта SmartOffice!

## Полная последовательность команд

```bash
# 1. Перейдите в папку проекта
cd C:\Users\1\Documents\Kiro\SmartOffice

# 2. Инициализируйте Git
git init

# 3. Добавьте все файлы
git add .

# 4. Создайте коммит
git commit -m "Initial commit: SmartOffice v1.0.0 - Complete HRM system with PostgreSQL"

# 5. Подключите GitHub репозиторий
git remote add origin https://github.com/rbehterev33-netizen/Kiro.git

# 6. Переименуйте ветку
git branch -M main

# 7. Отправьте изменения
git push -u origin main
```

## Если репозиторий уже существует

Если в репозитории уже есть файлы, используйте:

```bash
# Получите изменения с GitHub
git pull origin main --allow-unrelated-histories

# Отправьте ваши изменения
git push -u origin main
```

## Частые проблемы

### Ошибка: "fatal: remote origin already exists"

```bash
# Удалите существующий remote
git remote remove origin

# Добавьте заново
git remote add origin https://github.com/rbehterev33-netizen/Kiro.git
```

### Ошибка: "Updates were rejected"

```bash
# Принудительная отправка (осторожно!)
git push -u origin main --force
```

### Ошибка аутентификации

GitHub больше не поддерживает пароли. Используйте Personal Access Token:

1. Перейдите на GitHub: Settings → Developer settings → Personal access tokens
2. Создайте новый token с правами `repo`
3. Используйте token вместо пароля при push

Или используйте SSH ключи:

```bash
# Генерация SSH ключа
ssh-keygen -t ed25519 -C "your.email@example.com"

# Добавьте ключ на GitHub
# Settings → SSH and GPG keys → New SSH key
```

## Дальнейшая работа с Git

### Добавление новых изменений

```bash
# Посмотрите статус
git status

# Добавьте изменённые файлы
git add .

# Создайте коммит
git commit -m "Описание изменений"

# Отправьте на GitHub
git push
```

### Просмотр истории

```bash
# История коммитов
git log

# Краткая история
git log --oneline

# История с графом
git log --graph --oneline --all
```

### Создание веток

```bash
# Создать новую ветку
git checkout -b feature/new-feature

# Переключиться на ветку
git checkout main

# Слить ветку
git merge feature/new-feature
```

## Полезные команды

```bash
# Клонирование репозитория
git clone https://github.com/rbehterev33-netizen/Kiro.git

# Обновление из GitHub
git pull

# Просмотр удалённых репозиториев
git remote -v

# Отмена изменений
git checkout -- filename

# Отмена последнего коммита (сохранив изменения)
git reset --soft HEAD~1

# Просмотр изменений
git diff
```

## Структура коммитов (рекомендации)

Используйте понятные сообщения коммитов:

```bash
# Хорошие примеры
git commit -m "Add employee management module"
git commit -m "Fix salary calculation bug"
git commit -m "Update documentation for KPI module"
git commit -m "Refactor database triggers"

# Плохие примеры
git commit -m "fix"
git commit -m "update"
git commit -m "changes"
```

## .gitignore

Файл `.gitignore` уже создан и содержит:
- Системные файлы
- Логи
- Временные файлы
- Резервные копии БД
- Конфигурации с паролями

## README.md для GitHub

Файл `README.md` уже создан и будет автоматически отображаться на главной странице репозитория.

## Бейджи для README (опционально)

Добавьте в начало README.md:

```markdown
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)
```

## GitHub Actions (CI/CD)

Для автоматического тестирования создайте `.github/workflows/test.yml`:

```yaml
name: PostgreSQL Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Run database setup
      run: |
        cd scripts
        chmod +x deploy.sh
        ./deploy.sh
```

## Защита веток

На GitHub настройте защиту ветки `main`:
1. Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Включите:
   - Require pull request reviews
   - Require status checks to pass

## Лицензия

Проект использует MIT License - свободное использование для любых целей.

## Контакты

- GitHub: https://github.com/rbehterev33-netizen/Kiro
- Email: support@smartoffice.ru

---

**Готово!** После выполнения этих шагов ваш проект будет на GitHub! 🎉
