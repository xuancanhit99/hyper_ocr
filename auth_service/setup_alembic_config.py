# setup_alembic_config.py
import os
from dotenv import load_dotenv
import re


def setup_alembic_config():
    # Load biến môi trường từ .env
    load_dotenv()

    # Đọc template
    with open('alembic.ini.template', 'r') as f:
        template_content = f.read()

    # Thay thế các biến
    config_content = template_content.replace('${DB_USER}', os.getenv('DB_USER', ''))
    config_content = config_content.replace('${DB_PASSWORD}', os.getenv('DB_PASSWORD', ''))
    config_content = config_content.replace('${DB_HOST}', os.getenv('DB_HOST', ''))
    config_content = config_content.replace('${DB_PORT}', os.getenv('DB_PORT', ''))
    config_content = config_content.replace('${DB_NAME}', os.getenv('DB_NAME', ''))

    # Ghi ra file alembic.ini.template
    with open('alembic.ini', 'w') as f:
        f.write(config_content)


if __name__ == '__main__':
    setup_alembic_config()
