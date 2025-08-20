from flask import Flask, render_template, request, redirect, session, url_for
import json, os, random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
USER_DATA_FILE = 'users.json'

TASKS = {
    "Web Development": ["Build a simple HTML page", "Style your HTML page using CSS", "Add a contact form", "Create a responsive navbar", "Add animations using CSS or JS"],
    "Data Analysis": ["Import a dataset using pandas", "Clean null values", "Create a bar chart using matplotlib", "Analyze correlation between features", "Summarize insights from the data"],
    "Backend Development": ["Create a user login system", "Build a REST API using Flask", "Connect your API to SQLite", "Handle errors and exceptions", "Add user authentication"]
}

def load_users():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, 'r') as file:
        return json.load(file)

def save_users(users):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users, file, indent=4)

@app.route('/')
def home():
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']
        domain = request.form['domain']
        if username in users:
            return "Username already exists."
        if domain not in TASKS:
            return "Invalid domain selected."
        users[username] = {
            "password": password,
            "domain": domain,
            "tasks_completed": [],
            "assigned_tasks": []
        }
        save_users(users)
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['user'] = username
            return redirect('/dashboard')
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    users = load_users()
    user = session['user']
    data = users[user]
    domain = data['domain']
    completed = data['tasks_completed']
    assigned = data['assigned_tasks']
    total_tasks = len(TASKS[domain])
    progress = f"{len(completed)} / {total_tasks}"
    return render_template('dashboard.html', user=user, domain=domain, assigned=assigned, completed=completed, progress=progress)

@app.route('/assign')
def assign_task():
    if 'user' not in session:
        return redirect('/login')
    users = load_users()
    user = session['user']
    domain = users[user]['domain']
    completed = users[user]['tasks_completed']
    remaining = [task for task in TASKS[domain] if task not in completed]
    if not remaining:
        return "All tasks completed!"
    task = random.choice(remaining)
    users[user]['assigned_tasks'].append(task)
    save_users(users)
    return redirect('/dashboard')

@app.route('/complete', methods=['POST'])
def complete_task():
    if 'user' not in session:
        return redirect('/login')
    users = load_users()
    user = session['user']
    task = request.form['task']
    if task in users[user]['assigned_tasks']:
        users[user]['assigned_tasks'].remove(task)
        users[user]['tasks_completed'].append(task)
        save_users(users)
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
