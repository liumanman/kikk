from flask import Flask
from model.database import init_db

app = Flask(__name__)
init_db(app)

from rest.order import order_rest
from view.order import order_view

app.register_blueprint(order_rest)
app.register_blueprint(order_view)


if __name__ == '__main__':
	app.run()
