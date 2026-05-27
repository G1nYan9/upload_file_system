import os
from flask import Flask, request, render_template,session,flash,url_for,redirect,make_response

from config.settings import Config
from utils.db import get_db_con

app = Flask(__name__)
app.config.from_object(Config)


os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


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
            check_sql='select * from `unsafe_table` where ant=%s'
            cursor.execute(check_sql,(ant,))
            result=cursor.fetchone()
            if result :
                flash('该用户名已存在，请更换用户名')
                return redirect(url_for('register'))
            sql='insert into `unsafe_table`(ant,pwd) values(%s,%s)'
            cursor.execute(sql,(ant,pwd))
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
    con=None
    cur=None
    if not ant or not pwd:
        flash('can_not_be_empty')
        return redirect(url_for('login'))
    try:
        con=get_db_con()
        cur=con.cursor()
        check_sql=f"select * from `unsafe_table` where `ant`= '{ant}' and `pwd`='{pwd}'"
        print(check_sql)
        cur.execute(check_sql)
        result=cur.fetchone()
        print(result)
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
        if cur :
            cur.close()
        if con :
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
        if not file.content_type.startswith('image/'):
            flash('error_file_type')
            return redirect(url_for('upload'))
        save_path=os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(save_path)
        db=get_db_con()
        cursor=db.cursor()
        sql='insert into `unsafe_files`(username,filename,save_path,upload_time) values(%s,%s,%s,now())'
        cursor.execute(sql,(current_user,file.filename,save_path))
        db.commit()
        cursor.close()
        db.close()
        uploaded_file_url=f'/uploads/{file.filename}'
        return render_template('upload.html',logined_flag=True,uploaded_file_url=uploaded_file_url,upload_success=True)
    logined_flag=(current_user is not None)
    return render_template('upload.html',logined_flag=logined_flag,uploaded_file_url=uploaded_file_url,upload_success=upload_success)

@app.route('/uploads/<path:filename>')
def uploads(filename):
    try:
        file_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            filename
        )
        with open(file_path,'rb') as f:
            content = f.read()
        response = make_response(content)
        response.headers['Content-Type'] = 'image/jpeg'
        return response
    except Exception as e:
        return str(e)
    

if __name__ == '__main__':
    app.run()