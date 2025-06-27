

import uuid
from flask import Flask, redirect, render_template, request, jsonify, url_for, session



from app.connect_db import init_db, News, db_session, Media, File
from werkzeug.utils import secure_filename
from pathlib import Path

from app.models import HomeWork, GradeEnum, Role, Admin
from app.utils import check_file, file_type, read_db
import os
from sqlalchemy.orm import joinedload

from dotenv import load_dotenv, find_dotenv
from flask_security import SQLAlchemyUserDatastore, auth_required, hash_password, Security, current_user, roles_required
from flask_security.utils import verify_password, login_user


app = Flask(__name__)



BASE_DIR = Path(__file__).parent

UPLOAD_FOLDER = BASE_DIR / 'static'

VIDEO_PATH = UPLOAD_FOLDER / 'video'

PICTURE_PATH = UPLOAD_FOLDER

AUDIO_PATH = UPLOAD_FOLDER / 'audio'

DOCS_PATH = UPLOAD_FOLDER / 'docs'

# сократить может?: for cat in cat_list : {cat} : cat.lower()

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['VIDEO_PATH'] = VIDEO_PATH
app.config['PICTURE_PATH'] = PICTURE_PATH
app.config['AUDIO_PATH'] = AUDIO_PATH
app.config['DOCS_PATH'] = DOCS_PATH
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024
app.config['DEBUG'] = True


load_dotenv(find_dotenv())
URL = os.getenv('URL')

app.config['SQLALCHEMY_DATABASE_URI'] = URL
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT')
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'


class DBSessionWrapper:
    def __init__(self, session):
        self.session = session

db_wrapper = DBSessionWrapper(db_session)
user_datastore = SQLAlchemyUserDatastore(db_wrapper, Admin, Role)
security = Security(app, user_datastore)

admin_password = os.getenv('ADMIN_PASSWORD')


with app.app_context():
    init_db()

    admin_role = user_datastore.find_role('admin')
    if not admin_role:
        admin_role = user_datastore.create_role(name='admin')
        db_session.commit()

    admin_role = user_datastore.find_role('admin')

    if not security.datastore.find_user(email='sun82816@gmail.com'):
        admin_user = Admin(
            email='sun82816@gmail.com',
            password=admin_password,
            fs_uniquifier=str(uuid.uuid4()),
            phone_number='+79100091448'
        )
        admin_user.roles.append(admin_role)
        db_session.add(admin_user)
        db_session.commit()
        db_session.remove()
    
    
@app.context_processor
def utility_processor():
    def check_admin_role():
        return current_user.is_authenticated and current_user.has_role('admin')
    return dict(is_admin=check_admin_role)

app.config.update(
    MAX_VIDEO_SIZE=3 * 1024 * 1024 * 1024,  # 3 ГБ
    MAX_IMAGE_SIZE=50 * 1024 * 1024,        # 50 МБ
    MAX_AUDIO_SIZE=70 * 1024 * 1024,       # 70 МБ
    MAX_DOC_SIZE=30 * 1024 * 1024           # 30 МБ
)


MAIN_PAGE = "index.html"
MATERIALS = "materials.html"
NEWS = "news.html"
HT = "homework.html"
FILES = "files.html"



@app.context_processor
def inject_user():
    return dict(current_user=current_user)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

def upload_files(request):
        if request.method == 'POST':
             file = request.files['file']
             print(file, file.filename)
             bool_value, extension_name = check_file(file.filename)
             if file and bool_value: # True and True
                  filename = secure_filename(file.filename)
                  folder = file_type(extension_name)
                  full_path = os.path.join(app.config[folder], filename)
                  file.save(full_path)
                  file_model = File(file_path=full_path,
                                    file_type=folder,
                                    file_extension = extension_name)
                  
                  db_session.add(file_model)
                  db_session.commit()
                  
                  files = read_db(File)

                  
                  return files, file_model



@app.route("/")
def main_page():
    news_data = db_session.query(News).join(Media).order_by(Media.created_at.desc()).limit(3).all()
    homework_data = db_session.query(HomeWork).join(Media).order_by(Media.created_at.desc()).limit(3).all()
    return render_template(MAIN_PAGE, news=news_data, homework=homework_data)

@app.route('/materials')
def materials():
    return render_template(MATERIALS)

@app.route('/composers')
def composers():
    return render_template('composers.html')


# style_templates = {
#     'baroque': 'baroque.html',
#     'romantic': 'romantic.html',
#     'classical': 'classical.html',
#     'impressionism': 'impressionism.html',
#     'modern': 'modern.html'
# }

# @app.route('/<style>')
# def music_style(style):

#     template = style_templates.get(style)
#     return render_template(template)

@app.route('/baroque')
def baroque():
    return render_template('baroque.html')


@app.route('/video')
def video():
    return render_template('video.html')

@app.route('/theory')
def theory():
    return render_template('theory.html')

# @app.route('/news')
# def news():
#     return render_template(NEWS)

@app.route('/homework')
def home_task():
    return render_template(HT)

@app.route('/class/')
def clas():
    return render_template('class.html')


def read(table):
    data = db_session.query(table).all()
    return data

# если бы можно было бы объединить это все в отдельный класс, либо доработать мои crud операции


@app.route('/read_news/', methods=['GET'])
def read_news():
    news_data = db_session.query(News).join(Media).order_by(Media.created_at.desc()).all()
 
    return render_template(NEWS, news=news_data)



@app.route('/read_homework/', methods=['GET'])
def read_homework():

    grade_num = request.args.get('grade', type=int)

    print(grade_num)
    try:
        if grade_num is not None:
            homework_data = db_session.query(HomeWork).filter_by(grade=GradeEnum(grade_num).name).all()
    
        else:
            homework_data = read(HomeWork)    
    
    except ValueError:
        homework_data = []

   
    return render_template('class.html', homework=homework_data)


@app.route('/add_news/', methods=['GET'])
@auth_required()
@roles_required('admin')
def add_news():
    return render_template('create_news.html', is_homework=False, form_action=url_for('create_news'))

@app.route('/create_news/', methods=['POST'])
@auth_required()
@roles_required('admin')
def create_news():
    title = request.form.get('title')
    content = request.form.get('content')
    file = request.files.get('file')
 

    file_model = None
    if file:
        files, file_model = upload_files(request=request)
        
    
        media = Media(title=title, content=content)

        db_session.add_all([media, file_model])
        
        db_session.flush()
        print('МЕДИА ------------', media, media.id)
        
        news = News(media_id=media.id, file_id=file_model.id) 
        db_session.add(news)

        db_session.commit()
   

    else:
        media = Media(title=title, content=content)
        db_session.add(media)
        
        db_session.flush()
        print('МЕДИА ------------', media, media.id)
        news = News(media_id=media.id) 
  
        db_session.add(news)

        db_session.commit()


   
    return redirect(url_for('read_news'))
    
   #------дз-------------------------------------
@app.route('/add_homework/', methods=['GET'])
@roles_required('admin')
@auth_required()
def add_homework():
    return render_template('create_homework.html', is_homework=True, form_action=url_for('create_homework'), grade=GradeEnum)

@app.route('/create_homework/', methods=['POST'])
@roles_required('admin')
@auth_required()
def create_homework():
    title = request.form.get('title')
    content = request.form.get('content')
    class_number = int(request.form.get('class_number'))
    file = request.files.get('file')


    file_model = None
    if file:
        files, file_model = upload_files(request=request)
 
    
        media = Media(title=title, content=content)

        db_session.add_all([media, file_model])
        
        db_session.flush()
        print('МЕДИА ------------', media, media.id)
        
        homework = HomeWork(media_id=media.id, file_id=file_model.id, grade=GradeEnum(class_number).name) 
        db_session.add(homework)

        db_session.commit()
        

    else:
        media = Media(title=title, content=content)
        db_session.add(media)
        
        db_session.flush()
        print('МЕДИА ------------', media, media.id)
        homework = HomeWork(media_id=media.id, grade=GradeEnum(class_number).name) 
  
        db_session.add(homework)

        db_session.commit()
  

    
    return redirect(url_for('read_homework'))



@app.route('/read_file')
@roles_required('admin')
@auth_required()
def read_files():
    files = read_db(File)
                  
    return render_template('read.html',files=files)


@app.route('/files_upload', methods=['GET', 'POST'])
def upload():
    files = upload_files(request=request)
                  
    return render_template(FILES,files=files)


    return '''
                  <script>alert('Файл |', filename, '| успешно загружен')</script>
                  '''


@app.route('/news/<int:news_id>/', methods=['GET', 'POST'])
def news_id(news_id):
    # sql запрос SELECT * FROM news WHERE news_id = news_id
    news_one = db_session.query(News).filter_by(id=news_id).all()
    return render_template("news_id.html", news=news_one)

@app.route('/news_delete/<int:news_id>/', methods=['GET', 'POST'])
@roles_required('admin')
@auth_required()
def delete_news(news_id):
    db_session.query(News).filter_by(id=news_id).delete()
    db_session.commit()
    news = db_session.query(News).all()
    

    return render_template(NEWS, news=news)

def change_news(news_id):
    title = request.form.get('title')
    content = request.form.get('content')
    file = request.files.get('file')
    

    file_model = None
    if file:
        files, file_model = upload_files(request=request)
       
        media = Media(title=title, content=content)

        db_session.add_all([media, file_model])
        
        db_session.flush()
        print('МЕДИА ------------', media, media.id)
        
        news = News(media_id=media.id, file_id=file_model.id) 
        db_session.add(news)

        db_session.commit()
        

    else:
        media = Media(title=title, content=content)
        db_session.add(media)
        
        db_session.flush()
        print('МЕДИА ------------', media, media.id)
        news = News(media_id=media.id) 
  
        db_session.add(news)

        db_session.commit()
      
   
    return redirect(url_for('read_news'))



@app.route('/next_news/<int:news_id>/', methods=['GET', 'POST'])
def next_arrow(news_id):
    current_news = db_session.query(News).first()

    next_news = db_session.query(News).filter(News.id > news_id).order_by(News.id.asc()).first()



    if next_news is not None:
        return render_template('news_id.html', news=[next_news])
    else:
        return render_template('last.html')
    
@app.route('/previous_news/<int:news_id>/', methods=['GET', 'POST'])
def back_arrow(news_id):
    current_news = db_session.query(News).first()

    next_news = db_session.query(News).filter(News.id < news_id).order_by(News.id.desc()).first()



    if next_news is not None:
        return render_template('news_id.html', news=[next_news])
    else:
        return render_template('last.html')    



@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']

        current_user = db_session.query(Admin).filter_by(email=email).first()

        if current_user:
            session['email'] = email
            login_user(current_user)
            return redirect('profile.html')
        
       

@app.route('/profile/', methods=['GET'])
@auth_required()
def profile():
    email = session.get('email')
    user = db_session.query(Admin).filter_by(email=email).first()
    return render_template('profile.html', user=user)



@app.route('/game/')
def game():
    return render_template('games.html')



@app.route('/logout')
def logout():
    session.pop('email', None)
    session.clear()
    return redirect(url_for('main_page'))

if __name__ == '__main__':
    app.run(debug=True)
