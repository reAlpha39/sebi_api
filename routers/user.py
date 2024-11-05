from flask import abort
from flask import Blueprint, request, jsonify
from datetime import datetime
from models.user import UserModel
from schemas.user import validate_user_create, validate_user_update

user_bp = Blueprint('user', __name__)


@user_bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json()
    validated_data = validate_user_create(data)
    created_user = UserModel.create_user(validated_data)
    return jsonify({
        "status": "success",
        "message": "User successfully created",
        "data": created_user
    })


@user_bp.route('/', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    include_deleted = request.args.get('include_deleted', False, type=bool)
    search = request.args.get('search', None)
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    # Convert date strings to datetime objects if provided
    if from_date:
        from_date = datetime.fromisoformat(from_date)
    if to_date:
        to_date = datetime.fromisoformat(to_date)

    # Validate pagination parameters
    if page < 1:
        page = 1
    if limit < 1:
        limit = 1
    elif limit > 100:
        limit = 100

    users, total_records = UserModel.get_users(
        page, limit, include_deleted, search, from_date, to_date
    )

    total_pages = (total_records + limit - 1) // limit

    return jsonify({
        "status": "success",
        "data": users,
        "pagination": {
            "total_records": total_records,
            "total_pages": total_pages,
            "current_page": page,
            "limit": limit,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    })


@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    validated_data = validate_user_update(data)
    updated_user = UserModel.update_user(user_id, validated_data)
    return jsonify({
        "status": "success",
        "message": "User successfully updated",
        "data": updated_user
    })


@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    result = UserModel.delete_user(user_id)
    return jsonify(result)
