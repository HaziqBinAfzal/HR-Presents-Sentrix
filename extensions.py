from flask_mail import Mail
from flask_migrate import Migrate

mail = Mail()
migrate = Migrate(compare_type=True, render_as_batch=True)
