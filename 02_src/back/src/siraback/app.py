from siraback.config import app

# importando os blueprints
# equivalente a importar as rotas
from siraback.api.tenant import tenant_bp
from siraback.api.category import category_bp
from siraback.api.allowed_source import allowed_source_bp
from siraback.api.artifact import artifact_bp
from siraback.api.group import group_bp
from siraback.api.purpose import purpose_bp
from siraback.api.reservation import reservation_bp
from siraback.api.user import user_bp
from siraback.api.login import login_bp
from siraback.api.default import default_bp

# registrando os blueprints
app.register_blueprint(tenant_bp)
app.register_blueprint(category_bp)
app.register_blueprint(allowed_source_bp)
app.register_blueprint(artifact_bp)
app.register_blueprint(group_bp)
app.register_blueprint(purpose_bp)
app.register_blueprint(reservation_bp)
app.register_blueprint(user_bp)
app.register_blueprint(login_bp)
app.register_blueprint(default_bp)
