from flask import Blueprint

default_bp = Blueprint("default", __name__)

@default_bp.get("/")
def index():
    # resposta padrão para a rota raiz
    return {"myresult":"ok", 
            "mydetails":"Backend operante :-)"}