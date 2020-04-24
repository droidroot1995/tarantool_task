import logging
from logging.handlers import RotatingFileHandler

from app import app


if __name__ == '__main__':
    
    app.logger_name = 'kv_api.app'
    app.run(host='0.0.0.0', port='5000', debug=True)