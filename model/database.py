from flask_sqlalchemy import SQLAlchemy
from functools import partial

db = None


def init_db(app, uri='sqlite:///kikk.db'):
    global db
    if db is not None:
        return
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_ECHO'] = True
    db = SQLAlchemy(app, session_options={'autocommit': True})
    # db.create_session = create_session

    db.session.begin = partial(db.session.begin, subtransactions=True)

    from . import order
    from . import item
    from . import listing

    db.create_all()


# def create_session():
#     return SignallingSession(db, autocommit=True)
