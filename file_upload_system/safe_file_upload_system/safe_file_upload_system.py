import os
import hashlib
from flask import Flask, request, render_template,session,flash,url_for,redirect,send_from_directory
from werkzeug.utils import secure_filename
import uuid

from config.settings import Config
from utils.file_utils import allowed_file
from utils.db import get_db_con

app = Flask(__name__)
app.config.from_object(Config)


os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        ant=request.form.get('ant')
        pwd=request.form.get('pwd')
        if ant is None or pwd is None:
            flash('请输入用户名和密码')
            return redirect(url_for('register'))
        try:
            db=get_db_con()
            cursor=db.cursor()
            check_sql='select * from `pymysql_test` where ant=%s'
            cursor.execute(check_sql,(ant,))
            result=cursor.fetchone()
            if result :
                flash('该用户名已存在，请更换用户名')
                return redirect(url_for('register'))
            hashed_pwd=hash_password(pwd)
            sql='insert into `pymysql_test`(ant,pwd) values(%s,%s)'
            cursor.execute(sql,(ant,hashed_pwd))
            db.commit()
            flash('REDIRECT_TO_LOGIN')  # 【新增】发送一个特殊的跳转信号
        except Exception as e:
            db.rollback()
            flash('注册失败'+str(e))
            return redirect(url_for('register'))
        finally:
            cursor.close()
            db.close()

    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    ant = request.form.get('ant')
    pwd = request.form.get('pwd')
    if not ant or not pwd:
        flash('can_not_be_empty')
        return redirect(url_for('login'))
    try:
        con=get_db_con()
        cur=con.cursor()
        check_sql="select * from `pymysql_test` where `ant`=%s and `pwd`=%s"
        hashed_pwd=hash_password(pwd)
        cur.execute(check_sql,(ant,hashed_pwd))
        result=cur.fetchone()
        if result :
            session['user']=ant
            session.permanent=True
            flash('login_success_redirect')
            return redirect(url_for('login'))
        else:
            flash('login_failed')
            return redirect(url_for('login'))
    except Exception as e:
            flash('登录失败'+str(e))
            return redirect(url_for('login'))
    finally:
            cur.close()
            con.close()

@app.route('/profile')
def profile():
    current_user=session.get('user')
    return render_template('profile.html')

@app.route('/logout')
def logout():
    session.pop('user',None)
    flash('退出成功')
    return redirect(url_for('profile'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    current_user=session.get('user')
    uploaded_file_url=None
    upload_success=None
    if request.method == 'POST' and current_user is not None:
        if 'file' not in request.files:
            flash('not_file')
            return redirect(url_for('upload'))
        file=request.files['file']
        if file.filename=='':
            flash('did_not_select_file')
            return redirect(url_for('upload'))
        if file and allowed_file(file.filename):
            original_filename=file.filename
            saved_filename=str(uuid.uuid4())+'_'+secure_filename(file.filename)
            save_path=os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
            file.save(save_path)
            db=get_db_con()
            cursor=db.cursor()
            sql='insert into `user_files`(username,original_filename,saved_filename,file_path,upload_time) values(%s,%s,%s,%s,now())'
            cursor.execute(sql,(current_user,original_filename,saved_filename,save_path))
            db.commit()
            cursor.close()
            db.close()
            uploaded_file_url=f'/uploads/{saved_filename}'
            return render_template('upload.html',logined_flag=True,uploaded_file_url=uploaded_file_url,upload_success=True)
        else:
            flash('error_file_type')
            return redirect(url_for('upload'))
    logined_flag=(current_user is not None)
    return render_template('upload.html',logined_flag=logined_flag,uploaded_file_url=uploaded_file_url,upload_success=upload_success)

@app.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    

if __name__ == '__main__':
    app.run()