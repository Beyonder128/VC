d:\Ultron\CLG_PROGRAMS\CLG_PROGRAMS\EXPENSETRACKER\app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Expense {self.description}>'

# Routes
@app.route('/')
def index():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    total_expenses = sum(expense.amount for expense in expenses)
    
    # Calculate category totals
    categories = {}
    for expense in expenses:
        if expense.category not in categories:
            categories[expense.category] = 0
        categories[expense.category] += expense.amount
    
    return render_template('index.html', 
                         expenses=expenses, 
                         total_expenses=total_expenses,
                         categories=categories)

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        category = request.form['category']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        payment_method = request.form['payment_method']
        
        new_expense = Expense(
            description=description,
            amount=amount,
            category=category,
            date=date,
            payment_method=payment_method
        )
        
        db.session.add(new_expense)
        db.session.commit()
        
        flash('Expense added successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_expense.html')

@app.route('/edit_expense/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    
    if request.method == 'POST':
        expense.description = request.form['description']
        expense.amount = float(request.form['amount'])
        expense.category = request.form['category']
        expense.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        expense.payment_method = request.form['payment_method']
        
        db.session.commit()
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit_expense.html', expense=expense)

@app.route('/delete_expense/<int:id>')
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/filter_by_category/<category>')
def filter_by_category(category):
    expenses = Expense.query.filter_by(category=category).order_by(Expense.date.desc()).all()
    total_expenses = sum(expense.amount for expense in expenses)
    
    return render_template('index.html', 
                         expenses=expenses, 
                         total_expenses=total_expenses,
                         current_category=category)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)