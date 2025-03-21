# from flask import Flask

# def create_app():
#     """Create and configure the Flask application"""
#     app = Flask(__name__)
    
#     # Load configuration
#     app.config.from_object('app.config')
    
#     # Register blueprints
#     from app.routes import api_bp
#     app.register_blueprint(api_bp)
    
#     @app.route('/health')
#     def health_check():
#         """Health check endpoint"""
#         return {'status': 'healthy'}
    
#     return app
