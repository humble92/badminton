from flask import Flask, render_template, request, redirect, url_for, send_file
import os

app = Flask(__name__)
app.secret_key = os.getenv('secret_key')
PROGRAM = os.getenv('default_program')


@app.route('/')
def home():
    # for future usage, we build features at /search endpoint
    # instead of /
    return redirect(url_for('search'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html', program=PROGRAM)

    from scraper import scrape_item
    program = request.form['program']
    results = scrape_item(program=program)
    return render_template('search.html', program=program, results=results, total=len(results))

@app.route("/export")
def export():
  try:
    program = request.args.get('program')
    return send_file(f'programs_data/csv/{program}.csv')
  except:
    # just in case: after searching, csv file should exist
    return redirect("/")
