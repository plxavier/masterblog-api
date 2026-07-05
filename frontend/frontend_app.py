from flask import Flask, render_template
import sys
import os

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    app = Flask(__name__,
                static_folder=os.path.join(BASE_DIR, 'static'),
                template_folder=os.path.join(BASE_DIR, 'templates'))

    print("✅ Flask application created successfully")
    print(f"📁 Static folder: {os.path.join(BASE_DIR, 'static')}")
except Exception as error:
    print(f"Error creating Flask application: {error}")
    sys.exit(1)


@app.route('/', methods=['GET'])
def home():
    """
    Render the home page.
    Returns:
        Rendered HTML template index.html
    """
    try:
        return render_template("index.html")
    except Exception as error:
        print(f"Error rendering home page: {error}")
        return f"<h1>Error</h1><p>Unable to load the page. Please try again later.</p>", 500


#debug route
@app.route('/debug/static')
def debug_static():
    """Debug route to check static files."""
    import os
    try:
        static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        exists = os.path.exists(static_path)
        files = os.listdir(static_path) if exists else []
        return {
            "static_folder": static_path,
            "exists": exists,
            "files": files
        }
    except Exception as error:
        return {"error": str(error)}


if __name__ == '__main__':
    try:
        print("\n" + "=" * 50)
        print("🚀 Starting Frontend Server...")
        print("📍 Running on http://127.0.0.1:5001")
        print("=" * 50 + "\n")
        app.run(host="0.0.0.0", port=5001, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user.")
    except Exception as error:
        print(f"Error starting server: {error}")
        sys.exit(1)