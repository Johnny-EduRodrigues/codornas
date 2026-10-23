from siraback.models.login_provider import LoginProvider


def get_login_provider_by_name(name):
    return LoginProvider.query.filter_by(name=name).first()
