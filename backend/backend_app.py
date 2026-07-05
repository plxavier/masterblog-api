from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import sys
import logging

#logging
try:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
except Exception as error:
    print(f"Error configuring logging: {error}")
    sys.exit(1)

#app_creation
try:
    app = Flask(__name__, static_folder="../static")
    CORS(app)  # Enable CORS for all routes
    logger.info("Flask application created successfully")
except Exception as error:
    logger.error(f"Error creating Flask application: {error}")
    sys.exit(1)

#data_jsonformat
POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


#helper_functions
def find_post_by_id(posts, post_id):
    """
    Find a post by its ID.
    Args:
        posts: List of posts
        post_id: ID of the post to find
    Returns:
        Post object or None if not found
    """
    try:
        return next((post for post in posts if post['id'] == post_id), None)
    except Exception as error:
        logger.error(f"Error finding post by ID {post_id}: {error}")
        return None


#app_routes

@app.route('/')
def root():
    """
    GET /
        - Returns a welcome message and API links.
    """
    try:
        logger.info("Root accessed")
        return jsonify({
            "message": "Welcome to Masterblog API",
            "documentation": {
                "swagger_ui": "/api/docs",
                "api_info": "/api"
            },
            "quick_links": {
                "get_all_posts": "/api/posts",
                "create_post": "POST /api/posts",
                "get_post": "/api/posts/{id}",
                "update_post": "PUT /api/posts/{id}",
                "delete_post": "DELETE /api/posts/{id}",
                "search_posts": "/api/posts/search?title=query"
            }
        }), 200
    except Exception as error:
        logger.error(f"Error in root: {error}")
        return jsonify({"error": f"Error accessing root: {str(error)}"}), 500

@app.route('/api')
def api_root():
    """
    GET /api
        - Returns API information and available endpoints.
    """
    try:
        logger.info("API root accessed")
        return jsonify({
            "message": "Welcome to Masterblog API",
            "version": "1.0.0",
            "endpoints": {
                "GET /api": "This page (API information)",
                "GET /api/posts": "Get all posts (with sorting & pagination)",
                "POST /api/posts": "Create a new post",
                "GET /api/posts/{id}": "Get a specific post by ID",
                "PUT /api/posts/{id}": "Update a post by ID",
                "DELETE /api/posts/{id}": "Delete a post by ID",
                "GET /api/posts/search": "Search posts by title or content",
                "GET /api/docs": "Swagger UI documentation"
            },
            "parameters": {
                "GET /api/posts": {
                    "sort": "title or content",
                    "direction": "asc or desc (default: asc)",
                    "page": "page number (integer)",
                    "limit": "items per page (integer)"
                },
                "POST /api/posts": {
                    "title": "string (required)",
                    "content": "string (required)"
                },
                "PUT /api/posts/{id}": {
                    "title": "string (optional)",
                    "content": "string (optional)"
                },
                "GET /api/posts/search": {
                    "title": "string (optional)",
                    "content": "string (optional)"
                }
            },
            "example_requests": {
                "GET /api/posts": "curl http://127.0.0.1:5002/api/posts",
                "GET /api/posts?sort=title&direction=desc": "curl http://127.0.0.1:5002/api/posts?sort=title&direction=desc",
                "GET /api/posts?page=1&limit=2": "curl http://127.0.0.1:5002/api/posts?page=1&limit=2",
                "POST /api/posts": "curl -X POST http://127.0.0.1:5002/api/posts -H 'Content-Type: application/json' -d '{\"title\":\"New Post\",\"content\":\"Content here\"}'",
                "PUT /api/posts/1": "curl -X PUT http://127.0.0.1:5002/api/posts/1 -H 'Content-Type: application/json' -d '{\"title\":\"Updated Title\"}'",
                "DELETE /api/posts/1": "curl -X DELETE http://127.0.0.1:5002/api/posts/1",
                "GET /api/posts/search": "curl 'http://127.0.0.1:5002/api/posts/search?title=First'"
            }
        }), 200
    except Exception as error:
        logger.error(f"Error in api_root: {error}")
        return jsonify({"error": f"Error accessing API root: {str(error)}"}), 500


@app.route('/api/posts', methods=['GET', 'POST'])
def handle_posts():
    """
    GET /api/posts
        - Returns all posts.
        - Supports optional query parameters:
            * sort: 'title' or 'content'
            * direction: 'asc' or 'desc'
            * page: integer page number
            * limit: integer number of posts per page
    POST /api/posts
        - Creates a new post.
        - Expects JSON body with 'title' and 'content'.
        - Returns 201 Created with the created post.
        - Returns 400 Bad Request if required fields are missing.
    """
    try:
        if request.method == 'POST':
            try:
                data = request.get_json()
                title = data.get('title') if data else None
                content = data.get('content') if data else None

                # Validate required fields
                missing_fields = []
                if not title or not title.strip():
                    missing_fields.append("title")
                if not content or not content.strip():
                    missing_fields.append("content")

                if missing_fields:
                    logger.warning(f"Missing fields in POST request: {missing_fields}")
                    return jsonify({
                        "error": "Missing required fields",
                        "missing": missing_fields
                    }), 400

                new_post = {
                    "id": max((post['id'] for post in POSTS), default=0) + 1,
                    "title": data.get('title').strip(),
                    "content": data.get('content').strip()
                }
                POSTS.append(new_post)
                logger.info(f"New post created: {new_post['title']} (ID: {new_post['id']})")
                return jsonify(new_post), 201

            except Exception as error:
                logger.error(f"Error processing POST request: {error}")
                return jsonify({"error": f"Error creating post: {str(error)}"}), 400

        # GET request
        try:
            sort = request.args.get('sort')
            direction = request.args.get('direction', 'asc')

            # Validate sort params
            if (sort and sort not in ['title', 'content']) or (direction and direction not in ['asc', 'desc']):
                logger.warning(f"Invalid sort parameters: sort={sort}, direction={direction}")
                return jsonify({'error': 'Invalid sort fields or direction'}), 400

            posts = POSTS[:]

            # Apply sorting if needed
            if sort in ['title', 'content']:
                reverse = (direction == 'desc')
                posts = sorted(posts, key=lambda post: post[sort].lower(), reverse=reverse)

            # Pagination
            page = request.args.get('page', type=int)
            limit = request.args.get('limit', type=int)
            if page and limit:
                if page < 1 and limit < 1:
                    return jsonify({'error': 'Page and limit must be positive integers'}), 400
                start_index = (page - 1) * limit
                end_index = start_index + limit
                posts = posts[start_index:end_index]

            logger.info(f"GET request: returning {len(posts)} posts")
            return jsonify(posts), 200

        except Exception as error:
            logger.error(f"Error processing GET request: {error}")
            return jsonify({"error": f"Error retrieving posts: {str(error)}"}), 500

    except Exception as error:
        logger.error(f"Unexpected error in handle_posts: {error}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    DELETE /api/posts/<post_id>
        - Deletes a post by ID.
        - Returns 200 OK with a success message if the post was deleted.
        - Returns 404 Not Found if the post does not exist.
    """
    try:
        logger.info(f"DELETE request for post ID: {post_id}")
        post_to_delete = find_post_by_id(POSTS, post_id)

        if post_to_delete:
            POSTS.remove(post_to_delete)
            logger.info(f"Post {post_id} deleted successfully")
            return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200

        logger.warning(f"DELETE request failed: Post {post_id} not found")
        return jsonify({"message": "Requested post doesn't exist!"}), 404

    except Exception as error:
        logger.error(f"Error deleting post {post_id}: {error}")
        return jsonify({"error": f"Error deleting post: {str(error)}"}), 500


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    PUT /api/posts/<post_id>
        - Updates a post by ID.
        - Expects JSON body with optional 'title' and/or 'content'.
        - Returns 200 OK with the updated post if successful.
        - Returns 404 Not Found if the post does not exist.
    """
    try:
        logger.info(f"PUT request for post ID: {post_id}")
        post_to_update = find_post_by_id(POSTS, post_id)

        if not post_to_update:
            logger.warning(f"PUT request failed: Post {post_id} not found")
            return jsonify({"message": "Requested post doesn't exist!"}), 404

        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400

            title = data.get('title')
            content = data.get('content')
            updated = False

            if title is not None and isinstance(title, str) and title.strip():
                post_to_update['title'] = title.strip()
                updated = True
            if content is not None and isinstance(content, str) and content.strip():
                post_to_update['content'] = content.strip()
                updated = True

            if not updated:
                logger.warning("PUT request: No valid fields to update")
                return jsonify({"error": "No valid fields to update"}), 400

            logger.info(f"Post {post_id} updated successfully")
            return jsonify({
                "id": post_id,
                "title": post_to_update['title'],
                "content": post_to_update['content']
            }), 200

        except Exception as error:
            logger.error(f"Error parsing JSON in PUT request: {error}")
            return jsonify({"error": f"Error processing update: {str(error)}"}), 400

    except Exception as error:
        logger.error(f"Error updating post {post_id}: {error}")
        return jsonify({"error": f"Error updating post: {str(error)}"}), 500


@app.route('/api/posts/search', methods=['GET'])
def handle_search():
    """
    GET /api/posts/search
        - Searches posts by 'title' and/or 'content' query parameters.
        - Returns 200 OK with a list of posts matching the search terms.
        - Returns an empty list if no posts match.
    """
    try:
        title = request.args.get('title', '').strip()
        content = request.args.get('content', '').strip()

        logger.info(f"Search request - title: '{title}', content: '{content}'")

        if not title and not content:
            logger.info("Search with no parameters, returning empty list")
            return jsonify([]), 200

        results = [
            post for post in POSTS
            if (title and title.lower() in post['title'].lower())
               or (content and content.lower() in post['content'].lower())
        ]

        logger.info(f"Search found {len(results)} results")
        return jsonify(results), 200

    except Exception as error:
        logger.error(f"Error in search: {error}")
        return jsonify({"error": f"Error searching posts: {str(error)}"}), 500


#error_handling

@app.errorhandler(400)
def bad_request_error(error):
    logger.warning(f"400 Bad Request: {error}")
    return jsonify({'error': 'Bad request, missing some data'}), 400


@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f"404 Not Found: {request.url}")
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    logger.warning(f"405 Method Not Allowed: {request.method} {request.url}")
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Internal Server Error: {error}")
    return jsonify({"error": "Internal server error"}), 500

#debug_route
@app.route('/debug/static')
def debug_static():
    """Debug route to check static files."""
    import os
    try:
        # Check if static folder exists
        static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
        exists = os.path.exists(static_path)
        files = os.listdir(static_path) if exists else []
        return {
            "static_folder": static_path,
            "exists": exists,
            "files": files
        }
    except Exception as error:
        return {"error": str(error)}


#Swaager_setup
try:
    # Swagger UI Configuration
    SWAGGER_URL = "/api/docs"

    # ✅ Point to root static folder (outside backend)
    API_URL = "/static/masterblog.json"

    swagger_ui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            "app_name": "Masterblog API",
            "validatorUrl": None,
            "operationsSorter": "method",
            "tagsSorter": "alpha",
            "docExpansion": "list"
        }
    )
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
    logger.info("Swagger UI configured successfully")
    print("📚 Swagger UI available at: http://127.0.0.1:5002/api/docs")
except Exception as error:
    logger.error(f"Error configuring Swagger UI: {error}")

#main
if __name__ == '__main__':
    try:
        print("\n" + "=" * 50)
        print("Starting Masterblog API Server...")
        print("Running on http://127.0.0.1:5002")
        print("Running on http://0.0.0.0:5002")
        print("Swagger UI: http://127.0.0.1:5002/api/docs")
        print("=" * 50 + "\n")
        logger.info("Server starting on port 5002")
        app.run(host="0.0.0.0", port=5002, debug=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
        logger.info("Server stopped by user")
    except Exception as error:
        print(f"Error starting server: {error}")
        logger.error(f"Error starting server: {error}")
        sys.exit(1)
