from flask import Blueprint, request, jsonify, abort
from datetime import datetime
import asyncio
from models.user import UserModel
from schemas.user import UserCreate, UserUpdate

bp = Blueprint('user', __name__)


def run_async(coro):
    """Helper function to run async code in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@bp.route('/', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        user_data = UserCreate(**data)  # Validate using Pydantic model
        created_user = run_async(UserModel.create_user(user_data.model_dump()))
        return jsonify({
            "status": "success",
            "message": "User successfully created",
            "data": created_user
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@bp.route('/', methods=['GET'])
def get_users():
    try:
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

        users, total_records = run_async(UserModel.get_users(
            page, limit, include_deleted, search, from_date, to_date
        ))

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
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        user_data = UserUpdate(**data)  # Validate using Pydantic model
        updated_user = run_async(UserModel.update_user(
            user_id, user_data.model_dump()))
        return jsonify({
            "status": "success",
            "message": "User successfully updated",
            "data": updated_user
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        result = run_async(UserModel.delete_user(user_id))
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
