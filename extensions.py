from flask_mail import Mail
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect


mail = Mail()
csrf = CSRFProtect()
migrate = Migrate(compare_type=True, render_as_batch=True)
