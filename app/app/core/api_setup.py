from ..api.admin_routes import admin_api
from ..api.user_routes import users_api
from ..api.argorithm_routes import argorithms_api
from ..api.programmer_routes import programmers_api
from ..api.report_routes import reports_api

def compile_routes(app):
    app.include_router(admin_api)
    app.include_router(argorithms_api)
    app.include_router(programmers_api)
    app.include_router(users_api)
    app.include_router(reports_api)
