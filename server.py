from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from bs4 import BeautifulSoup
import bleach
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24).hex())

POSTS_DIR = 'posts'
UPLOAD_FOLDER = 'static/uploads'
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'supersecret')
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
    return redirect(url_for('login_page'))

# Homepage
@app.route('/')
def home():
    posts = []
    logger.debug(f"Reading posts from {POSTS_DIR}")
    try:
        if not os.path.exists(POSTS_DIR):
            logger.warning(f"Posts directory {POSTS_DIR} does not exist")
            return render_template('index.html', posts=posts)
        for fname in os.listdir(POSTS_DIR):
            if not fname.endswith('.html'):
                continue
            post_name = fname.replace('.html', '')
            logger.debug(f"Processing post: {post_name}")
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
    except PermissionError as e:
        logger.error(f"PermissionError in home route: {e}")
        abort(403)
    except Exception as e:
        logger.error(f"Error in home route: {e}")
        raise
    return render_template('index.html', posts=posts)

# Individual post
@app.route('/post/<post_name>')
def post(post_name):
    try:
        logger.debug(f"Accessing post: {post_name}")
        with open(f'{POSTS_DIR}/{post_name}.html', 'r', encoding='utf-8') as f:
            content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        title = soup.find('h1').get_text() if soup.find('h1') else post_name.replace('_', ' ')
        content_html = str(soup)  # Keep full content including <h1>
        thumb_path = None
        video_path = None
        audio_path = None
        meta_file = f'{POSTS_DIR}/{post_name}.html.meta'
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
        return render_template('post.html', title=title, content=content_html, thumbnail=thumb_path, video=video_path, audio=audio_path, date=formatted_date)
    except FileNotFoundError:
        return "Post not found", 404
    except PermissionError:
        abort(403)

# Project page
@app.route('/project')
def project():
    return render_template('project.html')

# Login page
@app.route('/login')
def login_page():
    return render_template('login.html')

# New post page
@app.route('/new_post')
def new_post_page():
    if not session.get('logged_in'):
        flash("Please log in to create a post.")
        return redirect(url_for('login_page'))
    return render_template('new_post.html')

# Login (POST)
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

# Logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash("Logged out successfully!")
    return redirect(url_for('home'))

# New post (POST)
@app.route('/new_post', methods=['POST'])
def new_post():
    if not session.get('logged_in'):
        logger.debug("Session not logged in, redirecting to login")
        abort(403)
    try:
        logger.debug(f"Received form data: {request.form}")
        logger.debug(f"Received files: {request.files}")
        title = request.form.get('title')
        if not title:
            raise ValueError("Title is required")
        content = request.form.get('body') or request.form.get('body_fallback')
        if not content or content.strip() == '<p><br></p>':
            raise ValueError("Post content cannot be empty")
        content = bleach.clean(
            content,
            tags=['p', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'h1', 'h2', 'h3', 'blockquote'],
            attributes={'a': ['href', 'title']},
            protocols=['http', 'https'],
            strip=True
        )
        logger.debug(f"Sanitized content: {content}")
        if not content:
            raise ValueError("Content was stripped by sanitization")
        filename = secure_filename(title.replace(' ', '_')) + '.html'

        thumb_filename = None
        thumbnail_file = request.files.get('thumbnail')
        if thumbnail_file and allowed_file(thumbnail_file.filename):
            thumb_filename = secure_filename(thumbnail_file.filename)
            logger.debug(f"Saving thumbnail: {thumb_filename}")
            thumbnail_file.save(os.path.join(app.config['UPLOAD_FOLDER'], thumb_filename))

        video_filename = None
        video_file = request.files.get('video')
        if video_file and allowed_file(video_file.filename):
            video_filename = secure_filename(video_file.filename)
            logger.debug(f"Saving video: {video_filename}")
            video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], video_filename))

        audio_filename = None
        audio_file = request.files.get('audio')
        if audio_file and allowed_file(audio_file.filename):
            audio_filename = secure_filename(audio_file.filename)
            logger.debug(f"Saving audio: {audio_filename}")
            audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], audio_filename))

        logger.debug(f"Writing post to: {POSTS_DIR}/{filename}")
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
            logger.debug(f"Writing meta to: {POSTS_DIR}/{filename}.meta")
            with open(f'{POSTS_DIR}/{filename}.meta', 'w', encoding='utf-8') as f:
                f.write('\n'.join(meta_content))

        flash("Post created successfully!")
        return redirect(url_for('post', post_name=filename.replace('.html', '')))
    except PermissionError as e:
        logger.error(f"PermissionError in new_post: {e}")
        flash("Failed to create post due to permission issues. Please try again.")
        return redirect(url_for('new_post_page'))
    except ValueError as e:
        logger.error(f"ValueError in new_post: {e}")
        flash(str(e))
        return redirect(url_for('new_post_page'))
    except Exception as e:
        logger.error(f"Error in new_post: {e}")
        flash("Failed to create post. Please try again.")
        return redirect(url_for('new_post_page'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)