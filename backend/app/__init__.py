import os
from flask import Flask, jsonify
from app.config import Config
from app.extensions import db, jwt, cors

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.institutions import institutions_bp
    from app.routes.students import students_bp
    from app.routes.uploads import uploads_bp
    from app.routes.verification import verification_bp
    from app.routes.duplicate_cases import duplicate_cases_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.enrolments import enrolments_bp
    from app.routes.reports import reports_bp
    from app.routes.notifications import notifications_bp
    from app.routes.users import users_bp
    from app.routes.audit_logs import audit_logs_bp
    from app.routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(institutions_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(uploads_bp)
    app.register_blueprint(verification_bp)
    app.register_blueprint(duplicate_cases_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(enrolments_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(audit_logs_bp)
    app.register_blueprint(settings_bp)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'AICTE APAAR-Based Student Data Management & Verification Portal',
            'version': '1.0.0'
        }), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not Found', 'message': 'The requested resource was not found'}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal Server Error', 'message': 'An unexpected server error occurred'}), 500

    return app
