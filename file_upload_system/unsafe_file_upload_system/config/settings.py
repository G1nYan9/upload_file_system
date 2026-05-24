import os

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    # Flask 密钥
    SECRET_KEY = 'G1nYan9' 
    
    # 数据库配置
    DB_HOST = 'localhost'
    DB_PORT = 3306
    DB_USER = 'root'
    DB_PASSWORD = 'root'
    DB_NAME = 'test'
    
    # 文件上传配置
    # 注意：这里路径指向项目根目录下的 static/uploads，方便静态文件访问
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads') 
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB