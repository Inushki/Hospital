from flask import render_template, request, redirect, url_for
from app import app

# Define the root route (homepage)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Process form data here
        return redirect(url_for('index'))
    return render_template('registration.html')

@app.route('/doctor_register', methods=['GET', 'POST'])
def doctor_register():
    if request.method == 'POST':
        # Process form data here
        return redirect(url_for('index'))
    return render_template('doctor_register.html')
