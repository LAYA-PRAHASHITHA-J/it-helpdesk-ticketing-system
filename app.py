from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tickets(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              issue TEXT NOT NULL,
              priority TEXT NOT NULL
        )             
    ''')
    conn.commit()
    conn.close()

def ensure_ticket_number_column():
    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()
    c.execute("PRAGMA table_info(tickets)")
    columns = [column[1] for column in c.fetchall()]
    if 'ticket_number' not in columns:
        c.execute("ALTER TABLE tickets ADD COLUMN ticket_number INTEGER")
        conn.commit()
    conn.close() 

def reset_ticket_numbers():
    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()
    c.execute("SELECT id FROM tickets ORDER BY id")
    rows = c.fetchall()
    for index, row in enumerate(rows, start=1):
        ticket_id = row[0]
        c.execute("UPDATE tickets SET ticket_number = ? WHERE id = ?", (index, ticket_id))
    conn.commit()
    conn.close()    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    issue = request.form['issue']
    priority = request.form['priority']

    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()
    c.execute('INSERT INTO tickets (name, issue, priority) VALUES (?, ?, ?)', (name, issue, priority))
    conn.commit()
    conn.close()
    reset_ticket_numbers()
    return redirect('/admin')

@app.route('/admin')
def admin():
    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tickets')
    tickets = c.fetchall()
    conn.close()
    ticket_with_numbers = [ticket + (i + 1,) for i, ticket in enumerate(tickets)]
    return render_template('admin.html', tickets=ticket_with_numbers)

@app.route('/delete/<int:id>')
def delete_ticket(id):
    conn = sqlite3.connect('tickets.db')
    c = conn.cursor()
    c.execute('DELETE FROM tickets WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    reset_ticket_numbers()
    return redirect('/admin')

if __name__ == '__main__':
    init_db()
    ensure_ticket_number_column()
    reset_ticket_numbers()
    app.run(debug=True)