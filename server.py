from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = "anothersecretkey"  # Change this

POSTS_DIR = 'posts'
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "supersecret"  # Change this
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(POSTS_DIR, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------------------
# Homepage
# ----------------------------
@app.route('/')
def home():
    posts = []
    for fname in os.listdir(POSTS_DIR):
        if not fname.endswith('.html'):
            continue
        post_name = fname.replace('.html','')
        # Load snippet
        with open(f'{POSTS_DIR}/{fname}', 'r', encoding='utf-8') as f:
            content = f.read()
        snippet = content[:120] + '...' if len(content) > 120 else content
        # Load thumbnail if exists
        thumb_path = None
        meta_file = f'{POSTS_DIR}/{fname}.meta'
        if os.path.exists(meta_file):
            with open(meta_file,'r',encoding='utf-8') as f:
                thumb_path = f.read().strip()
        # Get file modification date
        post_path = os.path.join(POSTS_DIR, fname)
        mod_time = os.path.getmtime(post_path)
        formatted_date = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M")
        posts.append({
            'name': post_name,
            'snippet': snippet,
            'thumbnail': thumb_path,
            'date': formatted_date
        })
    return render_template('index.html', posts=posts)

# ----------------------------
# Individual post
# ----------------------------
@app.route('/post/<post_name>')
def post(post_name):
    try:
        with open(f'{POSTS_DIR}/{post_name}.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # Load thumbnail if exists
        thumb_path = None
        meta_file = f'{POSTS_DIR}/{post_name}.html.meta'
        if os.path.exists(meta_file):
            with open(meta_file,'r',encoding='utf-8') as f:
                thumb_path = f.read().strip()

        return render_template('post.html', content=content, thumbnail=thumb_path)
    except FileNotFoundError:
        return "Post not found", 404

# ----------------------------
# Chat page
# ----------------------------
@app.route('/chat')
def chat():
    return render_template('chat.html')

# ----------------------------
# Admin login
# ----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash("Logged in successfully!")
            return redirect(url_for('new_post'))
        else:
            flash("Invalid credentials!")
            return redirect(url_for('login'))
    return render_template('login.html')

# ----------------------------
# Admin logout
# ----------------------------
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("Logged out successfully!")
    return redirect(url_for('home'))

# ----------------------------
# New post (admin only)
# ----------------------------
@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    if not session.get('logged_in'):
        flash("You must be logged in as admin to add posts.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        filename = title.replace(' ', '_') + '.html'

        # Save thumbnail if uploaded
        thumbnail_file = request.files.get('thumbnail')
        thumb_filename = None
        if thumbnail_file and allowed_file(thumbnail_file.filename):
            thumb_filename = secure_filename(thumbnail_file.filename)
            thumbnail_file.save(os.path.join(app.config['UPLOAD_FOLDER'], thumb_filename))

        # Save post content
        with open(f'{POSTS_DIR}/{filename}', 'w', encoding='utf-8') as f:
            f.write(f"<h1>{title}</h1>\n{content}")
        # Save thumbnail reference
        if thumb_filename:
            with open(f'{POSTS_DIR}/{filename}.meta', 'w', encoding='utf-8') as f:
                f.write(thumb_filename)

        flash("Post created successfully!")
        return redirect(url_for('home'))

    return render_template('new_post.html')

# ----------------------------
# Run server
# ----------------------------
if __name__ == '__main__':
    app.run(debug=True)
