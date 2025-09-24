@app.route('/new_post', methods=['POST'])
def new_post():
    if not session.get('logged_in'):
        abort(403)
    try:
        title = request.form['title']
        content = bleach.clean(
            request.form.get('body') or request.form.get('body_fallback'),
            tags=['p', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'h1', 'h2', 'h3', 'blockquote'],
            attributes={'a': ['href', 'title']},
            styles=[],
            protocols=['http', 'https'],
            strip=True
        )
        filename = secure_filename(title.replace(' ', '_')) + '.html'
        # ... (rest of the route unchanged)