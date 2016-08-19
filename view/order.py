from flask import Blueprint, render_template

order_view = Blueprint('order_view', __name__,
                       template_folder='templates',
                       static_url_path='static')


@order_view.route('/view/order', methods=['GET'])
def order_view_handler():
    return render_template('order_list.html')

# @order_view.route('/js/<path:path>')
