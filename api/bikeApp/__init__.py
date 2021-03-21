from .app import create_app
from .models import db, User

app = create_app()

from .views import *
