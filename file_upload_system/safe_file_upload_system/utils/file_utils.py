from config.settings import Config

def allowed_file(filename):
    """
    检查文件后缀是否合法
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS