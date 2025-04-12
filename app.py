from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'expense_db'

mysql = MySQL(app)

CATEGORIES = ["Food", "Transportation", "Utilities", "Entertainment", "Healthcare", "Shopping", "Others"]

@app.route('/', methods=['GET', 'POST'])
def index():
    filter_category = request.form.get('filter_category', 'All')
    search_note = request.form.get('search_note', '').strip()
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    query = "SELECT * FROM expenses WHERE 1"
    params = []

    if filter_category and filter_category != "All":
        query += " AND category = %s"
        params.append(filter_category)

    if search_note:
        query += " AND note LIKE %s"
        params.append(f"%{search_note}%")

    if start_date:
        query += " AND date >= %s"
        params.append(start_date)

    if end_date:
        query += " AND date <= %s"
        params.append(end_date)

    cur = mysql.connection.cursor()
    cur.execute(query, params)
    expenses = cur.fetchall()

    cur.execute("SELECT SUM(amount) FROM expenses")
    total_expense = cur.fetchone()[0] or 0

    cur.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    category_totals = cur.fetchall()

    return render_template('home.html',
                           expenses=expenses,
                           total_expense=total_expense,
                           category_totals=category_totals,
                           categories=CATEGORIES,
                           chart_labels=[row[0] for row in category_totals],
                           chart_data=[row[1] for row in category_totals],
                           selected_category=filter_category,
                           search_note=search_note,
                           start_date=start_date,
                           end_date=end_date)

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        category = request.form['category']
        note = request.form['note']
        amount = float(request.form['amount'])
        date = request.form['date']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO expenses (category, note, amount, date) VALUES (%s, %s, %s, %s)",
                    (category, note, amount, date))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))
    
    return render_template("add_expense.html", categories=CATEGORIES)

if __name__ == '__main__':
    app.run(debug=True)
