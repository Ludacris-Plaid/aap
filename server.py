<<<<<<< HEAD
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_frozen import Freezer
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from bs4 import BeautifulSoup
import bleach

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
freezer = Freezer(app)
=======
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = "anothersecretkey"  # Change this
>>>>>>> parent of b37a4d6 (initial commit)

POSTS_DIR = 'posts'
ADMIN_USERNAME = "admin"
<<<<<<< HEAD
ADMIN_PASSWORD = "supersecret"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'mp3', 'wav'}
=======
ADMIN_PASSWORD = "supersecret"  # Change this
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
>>>>>>> parent of b37a4d6 (initial commit)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(POSTS_DIR, exist_ok=True)

def allowed_file(filename):
<<<<<<< HEAD
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Custom 403 handler
@app.errorhandler(403)
def forbidden(e):
    flash("Access denied: Please log in as admin.")
    return redirect(url_for('login_page'))
=======
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS
>>>>>>> parent of b37a4d6 (initial commit)

# Homepage (freezable)
@app.route('/')
def home():
    posts = []
<<<<<<< HEAD
    try:
        for fname in os.listdir(POSTS_DIR):
            if not fname.endswith('.html'):
                continue
            post_name = fname.replace('.html', '')
            with open(f'{POSTS_DIR}/{fname}', 'r', encoding='utf-8') as f:
                content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            text_content = soup.get_text()
            snippet = text_content[:120] + '...' if len(text_content) > 120 else text_content
            thumb_path = None
            video_path = None
            audio_path = None
            meta_file = f'{POSTS_DIR}/{fname}.meta'
            if os.path.exists(meta_file):
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta_data = f.read().strip().split('\n')
                    for line in meta_data:
                        if line.startswith('thumbnail:'):
                            thumb_path = line[len('thumbnail:'):].strip()
                        elif line.startswith('video:'):
                            video_path = line[len('video:'):].strip()
                        elif line.startswith('audio:'):
                            audio_path = line[len('audio:'):].strip()
            post_path = os.path.join(POSTS_DIR, fname)
            mod_time = os.path.getmtime(post_path)
            formatted_date = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M")
            posts.append({
                'name': post_name,
                'snippet': snippet,
                'thumbnail': thumb_path,
                'video': video_path,
                'audio': audio_path,
                'date': formatted_date
            })
    except PermissionError:
        abort(403)
=======
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
>>>>>>> parent of b37a4d6 (initial commit)
    return render_template('index.html', posts=posts)

# Individual post (freezable)
@app.route('/post/<post_name>')
def post(post_name):
    try:
        with open(f'{POSTS_DIR}/{post_name}.html', 'r', encoding='utf-8') as f:
            content = f.read()
<<<<<<< HEAD
=======

        # Load thumbnail if exists
>>>>>>> parent of b37a4d6 (initial commit)
        thumb_path = None
        meta_file = f'{POSTS_DIR}/{post_name}.html.meta'
<<<<<<< HEAD
        post_path = os.path.join(POSTS_DIR, f'{post_name}.html')
        mod_time = os.path.getmtime(post_path)
        formatted_date = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M")
=======
>>>>>>> parent of b37a4d6 (initial commit)
        if os.path.exists(meta_file):
            with open(meta_file,'r',encoding='utf-8') as f:
                thumb_path = f.read().strip()

        return render_template('post.html', content=content, thumbnail=thumb_path)
    except FileNotFoundError:
        return "Post not found", 404
<<<<<<< HEAD
    except PermissionError:
        abort(403)

# Static pages (freezable)
@app.route('/login')
def login_page():
=======

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
>>>>>>> parent of b37a4d6 (initial commit)
    return render_template('login.html')

@app.route('/chat')
def chat_page():
    return render_template('chat.html', username='')

@app.route('/new_post')
def new_post_page():
    return render_template('new_post.html')

# Full login (non-freezable)
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['logged_in'] = True
        session['username'] = username
        flash("Logged in successfully!")
        return redirect(url_for('new_post_page'))
    else:
        flash("Invalid credentials!")
        return redirect(url_for('login_page'))

# Logout (non-freezable)
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
<<<<<<< HEAD
    session.pop('username', None)
=======
>>>>>>> parent of b37a4d6 (initial commit)
    flash("Logged out successfully!")
    return redirect(url_for('home'))

# New post (non-freezable)
@app.route('/new_post', methods=['POST'])
def new_post():
    if not session.get('logged_in'):
<<<<<<< HEAD
        abort(403)
    try:
        title = request.form['title']
        content = request.form['body']
        filename = secure_filename(title.replace(' ', '_')) + '.html'

        thumb_filename = None
        thumbnail_file = request.files.get('thumbnail')
=======
        flash("You must be logged in as admin to add posts.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        filename = title.replace(' ', '_') + '.html'

        # Save thumbnail if uploaded
        thumbnail_file = request.files.get('thumbnail')
        thumb_filename = None
>>>>>>> parent of b37a4d6 (initial commit)
        if thumbnail_file and allowed_file(thumbnail_file.filename):
            thumb_filename = secure_filename(thumbnail_file.filename)
            thumbnail_file.save(os.path.join(app.config['UPLOAD_FOLDER'], thumb_filename))

<<<<<<< HEAD
        video_filename = None
        video_file = request.files.get('video')
        if video_file and allowed_file(video_file.filename):
            video_filename = secure_filename(video_file.filename)
            video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], video_filename))

        audio_filename = None
        audio_file = request.files.get('audio')
        if audio_file and allowed_file(audio_file.filename):
            audio_filename = secure_filename(audio_file.filename)
            audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], audio_filename))

        with open(f'{POSTS_DIR}/{filename}', 'w', encoding='utf-8') as f:
            f.write(f"<h1>{title}</h1>\n{content}")

        meta_content = []
        if thumb_filename:
            meta_content.append(f"thumbnail:{thumb_filename}")
        if video_filename:
            meta_content.append(f"video:{video_filename}")
        if audio_filename:
            meta_content.append(f"audio:{audio_filename}")
        if meta_content:
            with open(f'{POSTS_DIR}/{filename}.meta', 'w', encoding='utf-8') as f:
                f.write('\n'.join(meta_content))

        flash("Post created successfully!")
        return redirect(url_for('home'))
    except PermissionError:
        abort(403)

# Register URLs for freezing
@freezer.register_generator
def post_generator():
    for fname in os.listdir(POSTS_DIR):
        if fname.endswith('.html'):
            post_name = fname.replace('.html', '')
            yield {'post_name': post_name}
=======
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
>>>>>>> parent of b37a4d6 (initial commit)

if __name__ == '__main__':
<<<<<<< HEAD
    app.run(debug=True)
=======
    app.run(debug=True)
>>>>>>> parent of b37a4d6 (initial commit)
