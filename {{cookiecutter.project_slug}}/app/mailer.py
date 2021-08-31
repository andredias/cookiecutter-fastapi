from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail
from jinja2 import Environment, FileSystemLoader

from . import config

templates_path = Path(__file__).parent / 'templates'
conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.DB_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME=config.MAIL_FROM_NAME,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    MAIL_DEBUG=config.DEBUG,
    SUPPRESS_SEND=config.DEBUG or config.TESTING,
    TEMPLATE_FOLDER=templates_path,
)

mailer = FastMail(conf)
loader = FileSystemLoader(templates_path)
templates = Environment(loader=loader, autoescape=True)
