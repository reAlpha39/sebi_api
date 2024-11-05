from quart import Blueprint, request, jsonify
from datetime import datetime
from models.user import UserModel
from schemas.user import validate_user_create, validate_user_update

user_bp = Blueprint('user', __name__)


@user_bp.route('/', methods=['POST'])
async def create_user():
    data = await request.get_json()
    validated_data = validate_user_create(data)
    created_user = await UserModel.create_user(validated_data)
    return jsonify({
        "status": "success",
        "message": "User successfully created",
        "data": created_user
    })


@user_bp.route('/', methods=['GET'])
async def get_users():
    args = request.args
    page = args.get('page', 1, type=int)
    limit = args.get('limit', 10, type=int)
    include_deleted = args.get('include_deleted', False, type=bool)
    search = args.get('search', None)
    from_date = args.get('from_date')
    to_date = args.get('to_date')

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

    users, total_records = await UserModel.get_users(
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
async def update_user(user_id):
    data = await request.get_json()
    validated_data = validate_user_update(data)
    updated_user = await UserModel.update_user(user_id, validated_data)
    return jsonify({
        "status": "success",
        "message": "User successfully updated",
        "data": updated_user
    })


@user_bp.route('/<int:user_id>', methods=['DELETE'])
async def delete_user(user_id):
    result = await UserModel.delete_user(user_id)
    return jsonify(result)
