import os

from flask import Flask, render_template, request, redirect, url_for, send_file, flash

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
        return render_template('search.html', program=PROGRAM, limit=1)

    from scraper import scrape_manager
    program = request.form['program']
    postcode = request.form['postcode']
    postcode = postcode.replace(' ', '').strip().lower()
    limit = int(request.form['limit'])
    try:  
        results = scrape_manager(postcode, program=program, limit=limit)
    except ValueError:
        flash('Invalid postal code.')
        return redirect(url_for('search'))

    return render_template('search.html', postcode=postcode, program=program, limit=limit, results=results,
                           total=len(results))


@app.route("/export")
def export():
    try:
        postcode = request.args.get('postcode')
        program = request.args.get('program')
        return send_file(f'data/output/csv/{postcode}-{program}.csv')
    except FileNotFoundError:
        # just in case: after searching, csv file should exist
        return redirect(url_for('search'))
