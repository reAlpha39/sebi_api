from flask import Blueprint, request, jsonify, abort
from datetime import datetime
import asyncio
from models.result import ResultModel
from schemas.result import ResultCreate, ResultUpdate, ResultResponse


bp = Blueprint('result', __name__)


def run_async(coro):
    """Helper function to run async code in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@bp.route('/', methods=['POST'])
def create_result():
    try:
        data = request.get_json()
        result_data = ResultCreate(**data)  # Validate input data
        created_result = run_async(
            ResultModel.create_result(result_data.model_dump()))
        response_data = ResultResponse(
            **created_result)  # Validate output data
        return jsonify({
            "status": "success",
            "message": "Result successfully created",
            "data": response_data.model_dump()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@bp.route('/', methods=['GET'])
def get_results():
    try:
        results = run_async(ResultModel.get_all_results())
        response_data = [ResultResponse(**result).model_dump()
                        for result in results]
        return jsonify({
            "status": "success",
            "message": "Results successfully retrieved",
            "data": response_data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@bp.route('/<int:result_id>', methods=['GET'])
def get_result(result_id):
    try:
        result = run_async(ResultModel.get_result_by_id(result_id))
        response_data = ResultResponse(**result).model_dump()
        return jsonify({
            "status": "success",
            "message": "Result successfully retrieved",
            "data": response_data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@bp.route('/<int:result_id>', methods=['PUT'])
def update_result(result_id):
    try:
        data = request.get_json()
        result_data = ResultUpdate(**data)  # Validate input data
        updated_result = run_async(ResultModel.update_result(
            result_id, result_data.model_dump(exclude_unset=True)))
        response_data = ResultResponse(**updated_result).model_dump()
        return jsonify({
            "status": "success",
            "message": "Result successfully updated",
            "data": response_data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@bp.route('/<int:result_id>', methods=['DELETE'])
def delete_result(result_id):
    try:
        run_async(ResultModel.delete_result(result_id))
        return jsonify({
            "status": "success",
            "message": "Result successfully deleted"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
