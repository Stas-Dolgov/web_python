<<<<<<< HEAD
import random
import secrets
import re
from flask import Flask, render_template, request, make_response, redirect,  url_for, session, flash
from faker import Faker
from werkzeug.exceptions import BadRequest
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user


fake = Faker()

app = Flask(__name__)
app.config['SECRET_KEY'] =  secrets.token_hex(16)
application = app

images_ids = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
              '2d2ab7df-cdbc-48a8-a936-35bba702def5',
              '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
              'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
              'cab5b7f2-774e-4884-a200-0c0180fa777f']

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Для доступа к этой странице необходимо пройти аутентификацию."

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password  

    def check_password(self, password):
        return check_password_hash(self.password, password)

users = {
    1: User(1, "user", generate_password_hash("qwerty"))
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

def generate_comments(replies=True):
    comments = []
    for i in range(random.randint(1, 3)):
        comment = { 'author': fake.name(), 'text': fake.text() }
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments

def generate_post(i):
    return {
        'title': 'Заголовок поста',
        'text': fake.paragraph(nb_sentences=100),
        'author': fake.name(),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'image_id': f'{images_ids[i]}.jpg',
        'comments': generate_comments()
    }

posts_list = sorted([generate_post(i) for i in range(5)], key=lambda p: p['date'], reverse=True)

def format_phone_number(phone_number):
    digits = re.sub(r'\D', '', phone_number)
    country_code = ""
    
    if len(digits) == 10:
        country_code = "+7"
    elif digits.startswith('7'):
        country_code = "+7"
        digits = digits[1:]
    elif digits.startswith('8'):
        country_code = "+7"
        digits = digits[1:]

    if len(digits) == 10 or (len(digits) == 11 and digits.startswith(('2', '3', '4', '5', '6', '7', '8', '9'))):
        return f"{country_code} ({digits[:3]}) {digits[3:6]}-{digits[6:8]}-{digits[8:10]}"

    else:
        return "Invalid phone number format"

def format_phone_number(phone_number):
    digits = re.sub(r'\D', '', phone_number)
    country_code = ""
    
    if len(digits) == 10:
        country_code = "+7"
    elif digits.startswith('7'):
        country_code = "+7"
        digits = digits[1:]
    elif digits.startswith('8'):
        country_code = "+7"
        digits = digits[1:]

    if len(digits) == 10 or (len(digits) == 11 and digits.startswith(('2', '3', '4', '5', '6', '7', '8', '9'))):
        return f"{country_code} ({digits[:3]}) {digits[3:6]}-{digits[6:8]}-{digits[8:10]}"

    else:
        return "Invalid phone number format"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts=posts_list)

@app.route('/posts/<int:index>', methods=['GET', 'POST'])
def post(index):
    if 0 <= index < len(posts_list):
        post = posts_list[index]

        if request.method == 'POST':
            comment_text = request.form.get('commentText')
            if comment_text:
                new_comment = {'author': fake.name(), 'text': comment_text, 'replies': []}
                post['comments'].append(new_comment)
                # Перенаправляем пользователя на ту же страницу после отправки комментария.
                return redirect(url_for('post', index=index))  # Добавлено перенаправление

        return render_template('post.html', title=post['title'], post=post)
    else:
        return "Post not found", 404

@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')

@app.route('/url_params/<path:path>')
def url_params(path):
    return render_template('url_params.html', path=path)

@app.route('/headers')
def headers():
    headers = request.headers
    return render_template('headers.html', headers=headers)

@app.route('/cookies')
def cookies():
    cookies = request.cookies
    return render_template('cookies.html', cookies=cookies)

@app.route('/form_params', methods=['GET', 'POST'])
def form_params():
    form_data = {}
    if request.method == 'POST':
        form_data = request.form
    return render_template('form_params.html', form_data=form_data)

@app.route('/phone', methods=['GET', 'POST'])
def phone():
    if request.method == 'POST':
        phone_number = request.form.get('phone')

        if not phone_number:
            return render_template('phone.html', error="Пожалуйста, введите номер телефона.", phone_number=phone_number)

        cleaned_number = re.sub(r'[()\s\-.]', '', phone_number)

        if not cleaned_number.isdigit():
            return render_template('phone.html', error="Недопустимый ввод. В номере телефона встречаются недопустимые символы.", phone_number=phone_number)

        if not (len(cleaned_number) == 10 or (len(cleaned_number) == 11 and cleaned_number.startswith(('7', '8')))):
            return render_template('phone.html', error="Недопустимый ввод. Неверное количество цифр.", phone_number=phone_number)

        formatted_number = format_phone_number(phone_number)
        return render_template('phone.html', formatted_number=formatted_number, phone_number=phone_number)

    return render_template('phone.html')

@app.route('/visits')
def visits():
    if 'visits' in session:
        session['visits'] = session.get('visits') + 1
    else:
        session['visits'] = 1
    return render_template('visits.html', visits=session['visits'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = next((u for u_id, u in users.items() if u.username == username), None)

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash("Вы успешно вошли!", "success")
            next_page = request.args.get('next')  
            return redirect(next_page or url_for('index'))
        else:
            flash("Неверный логин или пароль.", "danger")

    return render_template('login.html')

@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html')

if __name__ == "__main__":
    app.run(debug=True)
=======
import random
import secrets
import re
from flask import Flask, render_template, request, make_response, redirect,  url_for, session, flash
from faker import Faker
from werkzeug.exceptions import BadRequest
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user


fake = Faker()

app = Flask(__name__)
app.config['SECRET_KEY'] =  secrets.token_hex(16)
application = app

images_ids = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
              '2d2ab7df-cdbc-48a8-a936-35bba702def5',
              '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
              'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
              'cab5b7f2-774e-4884-a200-0c0180fa777f']

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Для доступа к этой странице необходимо пройти аутентификацию."

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password  

    def check_password(self, password):
        return check_password_hash(self.password, password)

users = {
    1: User(1, "user", generate_password_hash("qwerty"))
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

def generate_comments(replies=True):
    comments = []
    for i in range(random.randint(1, 3)):
        comment = { 'author': fake.name(), 'text': fake.text() }
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments

def generate_post(i):
    return {
        'title': 'Заголовок поста',
        'text': fake.paragraph(nb_sentences=100),
        'author': fake.name(),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'image_id': f'{images_ids[i]}.jpg',
        'comments': generate_comments()
    }

posts_list = sorted([generate_post(i) for i in range(5)], key=lambda p: p['date'], reverse=True)

def format_phone_number(phone_number):
    digits = re.sub(r'\D', '', phone_number)
    country_code = ""
    
    if len(digits) == 10:
        country_code = "+7"
    elif digits.startswith('7'):
        country_code = "+7"
        digits = digits[1:]
    elif digits.startswith('8'):
        country_code = "+7"
        digits = digits[1:]

    if len(digits) == 10 or (len(digits) == 11 and digits.startswith(('2', '3', '4', '5', '6', '7', '8', '9'))):
        return f"{country_code} ({digits[:3]}) {digits[3:6]}-{digits[6:8]}-{digits[8:10]}"

    else:
        return "Invalid phone number format"

def format_phone_number(phone_number):
    digits = re.sub(r'\D', '', phone_number)
    country_code = ""
    
    if len(digits) == 10:
        country_code = "+7"
    elif digits.startswith('7'):
        country_code = "+7"
        digits = digits[1:]
    elif digits.startswith('8'):
        country_code = "+7"
        digits = digits[1:]

    if len(digits) == 10 or (len(digits) == 11 and digits.startswith(('2', '3', '4', '5', '6', '7', '8', '9'))):
        return f"{country_code} ({digits[:3]}) {digits[3:6]}-{digits[6:8]}-{digits[8:10]}"

    else:
        return "Invalid phone number format"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts=posts_list)

@app.route('/posts/<int:index>', methods=['GET', 'POST'])
def post(index):
    if 0 <= index < len(posts_list):
        post = posts_list[index]

        if request.method == 'POST':
            comment_text = request.form.get('commentText')
            if comment_text:
                new_comment = {'author': fake.name(), 'text': comment_text, 'replies': []}
                post['comments'].append(new_comment)
                # Перенаправляем пользователя на ту же страницу после отправки комментария.
                return redirect(url_for('post', index=index))  # Добавлено перенаправление

        return render_template('post.html', title=post['title'], post=post)
    else:
        return "Post not found", 404

@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')

@app.route('/url_params/<path:path>')
def url_params(path):
    return render_template('url_params.html', path=path)

@app.route('/headers')
def headers():
    headers = request.headers
    return render_template('headers.html', headers=headers)

@app.route('/cookies')
def cookies():
    cookies = request.cookies
    return render_template('cookies.html', cookies=cookies)

@app.route('/form_params', methods=['GET', 'POST'])
def form_params():
    form_data = {}
    if request.method == 'POST':
        form_data = request.form
    return render_template('form_params.html', form_data=form_data)

@app.route('/phone', methods=['GET', 'POST'])
def phone():
    if request.method == 'POST':
        phone_number = request.form.get('phone')

        if not phone_number:
            return render_template('phone.html', error="Пожалуйста, введите номер телефона.", phone_number=phone_number)

        cleaned_number = re.sub(r'[()\s\-.]', '', phone_number)

        if not cleaned_number.isdigit():
            return render_template('phone.html', error="Недопустимый ввод. В номере телефона встречаются недопустимые символы.", phone_number=phone_number)

        if not (len(cleaned_number) == 10 or (len(cleaned_number) == 11 and cleaned_number.startswith(('7', '8')))):
            return render_template('phone.html', error="Недопустимый ввод. Неверное количество цифр.", phone_number=phone_number)

        formatted_number = format_phone_number(phone_number)
        return render_template('phone.html', formatted_number=formatted_number, phone_number=phone_number)

    return render_template('phone.html')

@app.route('/visits')
def visits():
    if 'visits' in session:
        session['visits'] = session.get('visits') + 1
    else:
        session['visits'] = 1
    return render_template('visits.html', visits=session['visits'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = next((u for u_id, u in users.items() if u.username == username), None)

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash("Вы успешно вошли!", "success")
            next_page = request.args.get('next')  
            return redirect(next_page or url_for('index'))
        else:
            flash("Неверный логин или пароль.", "danger")

    return render_template('login.html')

@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html')

if __name__ == "__main__":
    app.run(debug=True)
>>>>>>> b45a1e7f8d3d4195aed96e7e588c9814377a78f0
