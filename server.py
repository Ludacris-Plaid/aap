from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_socketio import SocketIO, emit
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from bs4 import BeautifulSoup
import bleach  # Optional: for sanitizing chat messages

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()  # Secure random key
socketio = SocketIO(app)

POSTS_DIR = 'posts'
UPLOAD_FOLDER = 'static/uploads'
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "supersecret"  # Change this
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'mp3', 'wav'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(POSTS_DIR, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Custom 403 handler
@app.errorhandler(403)
def forbidden(e):
    flash("Access denied: Please log in as admin.")
    return redirect(url_for('login'))

# ----------------------------
# Homepage
# ----------------------------
@app.route('/')
def home():
    print(f"Home route - Session: {session}")  # Debug
    posts = []
    try:
        for fname in os.listdir(POSTS_DIR):
            if not fname.endswith('.html'):
                continue
            post_name = fname.replace('.html', '')
            # Load content and generate snippet from body
            with open(f'{POSTS_DIR}/{fname}', 'r', encoding='utf-8') as f:
                content = f.read()
            # Strip HTML tags for snippet
            soup = BeautifulSoup(content, 'html.parser')
            text_content = soup.get_text()
            snippet = text_content[:120] + '...' if len(text_content) > 120 else text_content
            # Load metadata (thumbnail, video, audio)
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
            # Get file modification date
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
        print("PermissionError: Check permissions for posts/ directory")
        abort(403)
    return render_template('index.html', posts=posts)

# ----------------------------
# Individual post
# ----------------------------
@app.route('/post/<post_name>')
def post(post_name):
    print(f"Post route ({post_name}) - Session: {session}")  # Debug
    try:
        with open(f'{POSTS_DIR}/{post_name}.html', 'r', encoding='utf-8') as f:
            content = f.read()
        # Load metadata (thumbnail, video, audio)
        thumb_path = None
        video_path = None
        audio_path = None
        meta_file = f'{POSTS_DIR}/{post_name}.html.meta'
        # Get file modification date
        post_path = os.path.join(POSTS_DIR, f'{post_name}.html')
        mod_time = os.path.getmtime(post_path)
        formatted_date = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M")
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
        return render_template('post.html', content=content, thumbnail=thumb_path, video=video_path, audio=audio_path, date=formatted_date)
    except FileNotFoundError:
        return "Post not found", 404
    except PermissionError:
        print(f"PermissionError: Cannot access {post_path}")
        abort(403)

# ----------------------------
# Chat page
# ----------------------------
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    print(f"Chat route - Session: {session}")  # Debug
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            session['username'] = username
            print(f"Set username: {username}")  # Debug
        return redirect(url_for('chat'))
    return render_template('chat.html', username=session.get('username', ''))

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print(f"WebSocket connected - Session: {session}")  # Debug

@socketio.on('message')
def handle_message(data):
    username = session.get('username', 'Guest')
    is_admin = session.get('logged_in') and username == ADMIN_USERNAME
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = bleach.clean(data['message'], tags=['p', 'strong', 'em'], strip=True) if 'bleach' in globals() else data['message']
    print(f"Message from {username}: {message}")  # Debug
    emit('new_message', {
        'username': username,
        'message': message,
        'timestamp': timestamp,
        'is_admin': is_admin
    }, broadcast=True)

# ----------------------------
# Admin login
# ----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    print(f"Login route - Session before: {session}")  # Debug
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            print(f"Session after login: {session}")  # Debug
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
    print(f"Logout route - Session before: {session}")  # Debug
    session.pop('logged_in', None)
    session.pop('username', None)
    print(f"Session after logout: {session}")  # Debug
    flash("Logged out successfully!")
    return redirect(url_for('home'))

# ----------------------------
# New post (admin only)
# ----------------------------
@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    print(f"New post route - Session: {session}")  # Debug
    if not session.get('logged_in'):
        print("Access denied to /new_post: Not logged in")  # Debug
        abort(403)
    if request.method == 'POST':
        try:
            title = request.form['title']
            content = request.form['body']
            filename = secure_filename(title.replace(' ', '_')) + '.html'

            # Save thumbnail if uploaded
            thumb_filename = None
            thumbnail_file = request.files.get('thumbnail')
            if thumbnail_file and allowed_file(thumbnail_file.filename):
                thumb_filename = secure_filename(thumbnail_file.filename)
                thumbnail_file.save(os.path.join(app.config['UPLOAD_FOLDER'], thumb_filename))

            # Save video if uploaded
            video_filename = None
            video_file = request.files.get('video')
            if video_file and allowed_file(video_file.filename):
                video_filename = secure_filename(video_file.filename)
                video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], video_filename))

            # Save audio if uploaded
            audio_filename = None
            audio_file = request.files.get('audio')
            if audio_file and allowed_file(audio_file.filename):
                audio_filename = secure_filename(audio_file.filename)
                audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], audio_filename))

            # Save post content (title and body only)
            with open(f'{POSTS_DIR}/{filename}', 'w', encoding='utf-8') as f:
                f.write(f"<h1>{title}</h1>\n{content}")

            # Save metadata (thumbnail, video, audio)
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
            print("PermissionError: Check permissions for posts/ or uploads/ directories")
            abort(403)
    return render_template('new_post.html')

# ----------------------------
# Run server
# ----------------------------
if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)