from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # In production, use a proper secret key

# User credentials (username: password)
# In a real app, use proper password hashing and store in a database
USERS = {
    'vasiliy': 'vasiliy123',
    'diego': 'diego123',
    'user2': 'user2pass',
    'user3': 'user3pass',
    'user4': 'user4pass'
}

# Print credentials to console for Telegram distribution
print("=== DEFAULT CREDENTIALS ===")
for username, password in USERS.items():
    print(f"{username}:{password}")
print("===========================")

def get_telegram_logs():
    """Concatenate all memory/*.md files"""
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'memory')
    logs = []
    if os.path.exists(log_dir):
        for filename in sorted(os.listdir(log_dir)):
            if filename.endswith('.md'):
                filepath = os.path.join(log_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        logs.append(f"--- {filename} ---\n")
                        logs.append(f.read())
                        logs.append("\n\n")
                except Exception as e:
                    logs.append(f"Error reading {filename}: {e}\n\n")
    else:
        logs.append("Memory directory not found.\n")
    return ''.join(logs) if logs else "No log files found."

# Executor information (agents)
EXECUTORS = [
    {
        'id': 'director',
        'name': 'Director',
        'title': 'Директор Василий',
        'description': 'Директор компании, контроллер исполнения задач, предоставляет информацию о делах любого пользователя любому другому.',
        'status': 'Готов к работе',
        'last_task': 'Настройка голосовых команд (Vosk + Piper)',
        'icon': '👔'
    },
    {
        'id': 'researcher',
        'name': 'Researcher',
        'title': 'Исследователь',
        'description': 'Веб‑поиск, сбор и анализ информации, суммаризация данных.',
        'status': 'В разработке',
        'last_task': 'Планирование',
        'icon': '🔍'
    },
    {
        'id': 'programmer',
        'name': 'Programmer',
        'title': 'Программист',
        'description': 'Написание и редактирование кода, автоматизация задач, работа с файлами.',
        'status': 'В разработке',
        'last_task': 'Создание веб‑сервера с авторизацией',
        'icon': '💻'
    },
    {
        'id': 'analyst',
        'name': 'Analyst',
        'title': 'Аналитик',
        'description': 'Обработка данных, создание отчётов, визуализация.',
        'status': 'В разработке',
        'last_task': 'Планирование',
        'icon': '📊'
    },
    {
        'id': 'communicator',
        'name': 'Communicator',
        'title': 'Коммуникатор',
        'description': 'Общение с внешними сервисами, отправка сообщений, голосовое взаимодействие.',
        'status': 'В разработке',
        'last_task': 'Планирование',
        'icon': '📢'
    },
    {
        'id': 'organizer',
        'name': 'Organizer',
        'title': 'Организатор',
        'description': 'Управление задачами, напоминания, календарь.',
        'status': 'В разработке',
        'last_task': 'Планирование',
        'icon': '📅'
    },
    {
        'id': 'financier',
        'name': 'Financier',
        'title': 'Финансист',
        'description': 'Анализ финансовых рынков, инвестиций, отчётов. Специалист по золоту, нефти, биткоину.',
        'status': 'Активен',
        'last_task': 'Анализ золота, нефти, биткоина (март 2026)',
        'icon': '💰'
    }
]

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in USERS and USERS[username] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    # Show executors instead of users
    return render_template('dashboard.html', username=username, executors=EXECUTORS)

@app.route('/view_logs')
def view_logs():
    if 'username' not in session:
        return redirect(url_for('login'))
    logs = get_telegram_logs()
    return render_template('logs.html', logs=logs)

@app.route('/structure')
def structure():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('structure.html', executors=EXECUTORS)

@app.route('/financier_reports')
def financier_reports():
    if 'username' not in session:
        return redirect(url_for('login'))
    # Читаем файл отчётов
    reports_path = os.path.join(os.path.dirname(__file__), '..', 'financier_reports.md')
    reports_content = ""
    if os.path.exists(reports_path):
        with open(reports_path, 'r', encoding='utf-8') as f:
            reports_content = f.read()
    return render_template('financier_reports.html', reports=reports_content)

@app.route('/financier_reports_list')
def financier_reports_list():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    import glob, os, shutil
    from datetime import datetime
    
    workspace_dir = os.path.join(os.path.dirname(__file__), '..')
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    # Ensure static_dir exists
    os.makedirs(static_dir, exist_ok=True)
    
    reports = []
    seen = set()
    
    # Process PDF files from workspace
    for filepath in glob.glob(os.path.join(workspace_dir, '*.pdf')):
        filename = os.path.basename(filepath)
        if filename in seen:
            continue
        seen.add(filename)
        mtime = os.path.getmtime(filepath)
        date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
        static_path = os.path.join(static_dir, filename)
        if not os.path.exists(static_path):
            shutil.copy2(filepath, static_path)
        url = f'/static/{filename}'
        reports.append({'date': date_str, 'name': filename, 'url': url, 'type': 'PDF'})
    
    # Process MD report files from workspace
    md_patterns = [
        os.path.join(workspace_dir, '*отчёт*.md'),
        os.path.join(workspace_dir, '*report*.md'),
        os.path.join(workspace_dir, '*анализ*.md'),
        os.path.join(workspace_dir, '*прогноз*.md'),
    ]
    for pattern in md_patterns:
        for filepath in glob.glob(pattern):
            filename = os.path.basename(filepath)
            if filename in seen:
                continue
            seen.add(filename)
            mtime = os.path.getmtime(filepath)
            date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
            static_path = os.path.join(static_dir, filename)
            if not os.path.exists(static_path):
                shutil.copy2(filepath, static_path)
            url = f'/static/{filename}'
            title = filename
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('# '):
                        title = first_line[2:].strip()
            except:
                pass
            reports.append({'date': date_str, 'name': title, 'url': url, 'type': 'Markdown'})
    
    reports.sort(key=lambda x: x['date'], reverse=True)
    return render_template('financier_reports_list.html', reports=reports)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)