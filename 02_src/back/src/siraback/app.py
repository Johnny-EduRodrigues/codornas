from siraback.config import app

# importando os blueprints
# equivalente a importar as rotas
from siraback.api.tenant import tenant_bp
from siraback.api.login import login_bp
from siraback.api.default import default_bp

# registrando os blueprints
app.register_blueprint(tenant_bp)
app.register_blueprint(login_bp)
app.register_blueprint(default_bp)
