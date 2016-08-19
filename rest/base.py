from flask import Blueprint, request, jsonify, make_response


base_rest = Blueprint('base_rest', __name__)


@base_rest.errorhandler(Exception)
def internal_server_error(e):
    print('got error')
    return jsonify(error=str(e)), 500
