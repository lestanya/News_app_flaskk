import os
from werkzeug.utils import secure_filename
from app.connect_db import init_db, News, db_session, Base, Media, File
import app

FILE_EXTENSIONS = {
    'picture': ['jpg', 'jpeg', 'png', 'svg', 'gif', 'bmp', 'webp', 'tiff'],
    'video': ['mp4', 'mkv', 'mov', 'avi', 'wmv', 'flv', 'webm', 'mpeg'],
    'audio': ['mp3', 'wav', 'aac', 'ogg', 'flac', 'wma', 'm4a', 'aiff'],
    'docs': ['docx', 'doc', 'pdf', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'csv',
             'ppt', 'pptx', 'pub', 'epub']
}

def check_file(file_path):
    extension_values = [v for value in FILE_EXTENSIONS.values() for v in value]
    full_path = file_path.rsplit('.', 1)[0].lower()
    extension_name = file_path.rsplit('.', 1)[1].lower()

    return ('.' in file_path and extension_name in extension_values), extension_name


def file_type(file):
    try:
        if file in FILE_EXTENSIONS['picture']:
            return 'PICTURE_PATH' 
        
        if file in FILE_EXTENSIONS['video']:
            return 'VIDEO_PATH'
        
        if file in FILE_EXTENSIONS['audio']:
            return 'AUDIO_PATH'
        
        if file in FILE_EXTENSIONS['docs']:
            return 'DOCS_PATH'
    
    except KeyError:
        return 'Папки для такого типа файлов не сущетствует'
    

def read_db(table_name):
    objects = db_session.query(table_name).all()

    return objects         
 

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

    
                  
        # return render_template(FILES)
        # return '''
        #           <script>alert('Файл |', filename, '| успешно загружен')</script>
        #           '''
                     # return render_template('read.html',files=files)
# @app.route('/files')
# # @login_required
# def get_files():
#     files = db_session.query(File).all()
#     for file in files:
#          print(file)
#     return render_template(FILES, files=files)

# @app.route('/files', methods=['GET', 'POST'])