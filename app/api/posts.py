from app import db
from app.api import bp
from app.api.errors import bad_request
from app.models import Post
from flask import jsonify, request, url_for
from datetime import datetime

@bp.route('/posts/<int:id>', methods=['GET'])
def get_post(id):
    # get the post specified by the id
    return jsonify(Post.query.get_or_404(id).to_dict())

@bp.route('/posts/by_user/<int:user_id>', methods=['GET'])
def get_posts(user_id):
    # get all the posts from the specified user_id
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Post.to_collection_dict(Post.query.filter_by(user_id=user_id), page, per_page, 'api.get_posts', user_id=user_id)
    return jsonify(data)

@bp.route('/posts', methods=['GET'])
def get_all_posts():
    # get all the posts from all the users
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Post.to_collection_dict(Post.query, page, per_page, 'api.get_all_posts')
    return jsonify(data)
    
@bp.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json() or {}
    if 'body' not in data or 'user_id' not in data:
        return bad_request("You must include a body and a user ID.")
    post = Post()
    post.from_dict(data)
    db.session.add(post)
    db.session.commit()
    response = jsonify(post.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_post', id=post.id)
    return response

@bp.route('/posts/<int:id>', methods=['PUT'])
def update_post(id):
    post = Post.query.get_or_404(id)
    data = request.get_json() or {}
    if 'body' not in data:
        return bad_request("You must add a 'body' to the request.")
    post.from_dict(data)
    db.session.commit()
    return jsonify(post.to_dict())

@bp.route('/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    response = jsonify(post.to_dict())
    return response