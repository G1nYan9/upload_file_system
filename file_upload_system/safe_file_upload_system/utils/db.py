from pymysql import Connection
from config.settings import Config

def get_db_con():
    """
    创建并返回数据库连接对象
    """
    return Connection(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )