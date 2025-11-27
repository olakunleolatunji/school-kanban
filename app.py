import sqlite3
from flask import Flask, render_template, request, jsonify, g

app = Flask(__name__)
DATABASE = 'kanban.db'

# --- Database Helper Functions ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row # Allows accessing columns by name
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database table if it doesn't exist."""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course TEXT NOT NULL,
                content TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('todo', 'doing', 'reviewing', 'done'))
            )
        ''')
        db.commit()

# --- Routes ---

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    # IMPORTANT: We must order by course for the Jinja groupby to work correctly
    cursor.execute('SELECT * FROM tasks ORDER BY course ASC, id DESC')
    tasks = cursor.fetchall()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    """Adds a new row. Accepts optional 'course' to add to specific group."""
    db = get_db()
    cursor = db.cursor()
    
    # Check if a specific course name was passed
    data = request.get_json(silent=True) or {}
    course_name = data.get('course', '')
    
    # Defaults: Specified course (or empty), Empty content, Status 'todo'
    cursor.execute('INSERT INTO tasks (course, content, status) VALUES (?, ?, ?)', 
                   (course_name, '', 'todo'))
    db.commit()
    return jsonify({'success': True})

@app.route('/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    """Updates text content for course or task details."""
    data = request.json
    field = data.get('field') # 'course' or 'content'
    value = data.get('value')
    
    if field not in ['course', 'content']:
        return jsonify({'success': False, 'error': 'Invalid field'}), 400

    db = get_db()
    cursor = db.cursor()
    query = f'UPDATE tasks SET {field} = ? WHERE id = ?'
    cursor.execute(query, (value, task_id))
    db.commit()
    return jsonify({'success': True})

@app.route('/move/<int:task_id>', methods=['POST'])
def move_task(task_id):
    """Moves task forward or backward."""
    data = request.json
    direction = data.get('direction') # 'next' or 'prev'
    
    # Define the order of columns
    stages = ['todo', 'doing', 'reviewing', 'done']
    
    db = get_db()
    cursor = db.cursor()
    
    # Get current status
    cursor.execute('SELECT status FROM tasks WHERE id = ?', (task_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'success': False, 'error': 'Task not found'}), 404
        
    current_status = row['status']
    current_index = stages.index(current_status)
    
    new_index = current_index
    if direction == 'next' and current_index < len(stages) - 1:
        new_index += 1
    elif direction == 'prev' and current_index > 0:
        new_index -= 1
        
    new_status = stages[new_index]
    
    cursor.execute('UPDATE tasks SET status = ? WHERE id = ?', (new_status, task_id))
    db.commit()
    
    return jsonify({'success': True, 'new_status': new_status})

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    db.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db() # Ensure DB exists on startup
    app.run(debug=True)