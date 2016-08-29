from flask_sqlalchemy import SQLAlchemy
from functools import partial
# from flask_sqlalchemy import SignallingSession


def init_db(app, uri='sqlite:///kikk.db'):
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_ECHO'] = True
    global db
    db = SQLAlchemy(app, session_options={'autocommit': True})
    # db.create_session = create_session

    db.session.begin = partial(db.session.begin, subtransactions=True)

    from . import order
    from . import item
    from . import listing

    db.create_all()


# def create_session():
#     return SignallingSession(db, autocommit=True)
