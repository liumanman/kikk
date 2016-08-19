from flask import Blueprint, request, jsonify, make_response
from service.order import query_by, update_order

order_rest = Blueprint('order_rest', __name__)


@order_rest.route('/order', methods=['GET'])
def query():
    filters = {'order_date': [None, None],
               'shipping_date': [None, None]}
    for k, v in request.args.items():
        # v = Request.args[k]
        if k == 'order_date_from':
            filters['order_date'][0] = v
        elif k == 'order_date_to':
            filters['order_date'][1] = v
        elif k == 'shipping_date_from':
            filters['shipping_date'][0] = v
        elif k == 'shipping_date_to':
            filters['shipping_date'][1] = v
        else:
            filters[k] = v

    orders = query_by(**filters)
    order_list = list(map(lambda x: x.to_dict(show_all=True), orders))
    return jsonify(result=order_list)


@order_rest.route('/order', methods=['PUT'])
def update():
    order = request.get_json()
    print(order)
    update_order(order['order_id'], order['status'], order['memo'], *order['tracking_numbers'])
    resp = make_response()
    return resp

@order_rest.after_request
def after_reqeust(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


@order_rest.errorhandler(Exception)
def internal_server_error(e):
    # raise e
    return jsonify(error=str(e)), 500
