from flask import Flask, render_template, request, redirect, make_response, jsonify, url_for
import os
import socket
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/avatars'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

messages = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_local_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

@app.route('/', methods=['GET'])
def index():
    username = request.cookies.get('username')
    if not username:
        return redirect('/setname')
    return render_template('chat.html', username=username)

@app.route('/setname', methods=['GET', 'POST'])
def set_name():
    if request.method == 'POST':
        username = request.form['username']
        resp = make_response(redirect('/'))
        resp.set_cookie('username', username)
        return resp
    return render_template('setname.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    username = request.cookies.get('username')
    avatar = request.cookies.get('avatar')
    if not username:
        return redirect('/setname')
    if request.method == 'POST':
        new_username = request.form.get('username', username)
        remove_avatar = request.form.get('remove_avatar')
        file = request.files.get('avatar_file')
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('username', new_username)
        if remove_avatar:
            resp.set_cookie('avatar', '', expires=0)
        elif file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            resp.set_cookie('avatar', filename)
        return resp
    return render_template('settings.html', username=username, avatar=avatar)

@app.route('/send', methods=['POST'])
def send_message():
    username = request.cookies.get('username')
    avatar = request.cookies.get('avatar')
    if not username:
        return redirect('/setname')
    message = request.form['message']
    messages.append({
        'username': username,
        'message': message,
        'avatar': avatar
    })
    return redirect('/')

@app.route('/messages')
def get_messages():
    return jsonify(messages)

if __name__ == '__main__':
    ip = get_local_ip()
    print(f"Откройте в браузере: http://{ip}:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
