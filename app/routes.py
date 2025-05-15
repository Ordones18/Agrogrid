from flask import render_template
from app import app

@app.route('/')
def index():
    return render_template('index.html')

from flask import render_template
from app import app
@app.route('/explore')
def explore():
    return render_template('explore.html')