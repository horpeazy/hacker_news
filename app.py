# ----------------------------------------------------------------- #
# Imports
# ----------------------------------------------------------------- #
import sys
import os
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    abort
    )
import logging
import requests
from requests.exceptions import ConnectionError
from werkzeug.exceptions import NotFound
from dotenv import load_dotenv
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from flask_cors import CORS
from flask_apscheduler import APScheduler
from functions import paginate_news, populate_instance
from models import *

# -------------------------------------------------------------------- #
# App Config.
# -------------------------------------------------------------------- #
app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
db.create_all(app=app)
migrate = Migrate(app, db)

# --------------------------------------------------------------------- #
# CORS
# --------------------------------------------------------------------- #
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.after_request
def after_request(response):
    response.headers.add(
        "Access-Control-Allow-Headers", "Content-Type"
    )
    response.headers.add(
        "Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS,PATCH,"
    )
    return response

# -------------------------------------------------------------------- #
# URL Parameters
# -------------------------------------------------------------------- #


load_dotenv()
item_url = os.getenv("ITEM_URL")
max_item_url = os.getenv("MAX_ITEM_URL")
update_url = os.getenv("UPDATE_URL")


# ---------------------------------------------------------------------#
# Scheduler.
# ---------------------------------------------------------------------#


scheduler = APScheduler()
scheduler.init_app(app)


def fetch_max():
    ''' Fetch the maximum id of items present
        in Hacker News Database
    '''
    try:
        res = requests.get(max_item_url)
        if res.status_code == 200:
            return res.json()
        else:
            return None
    except Exception:
        print(sys.exc_info())


def fetch_data(min, max):
    """ Fetch data from Hacker News API and
        update database
    """
    try:
        # Add latest items to a session
        for i in range(min, max):
            res = requests.get(item_url.format(i))
            if res.status_code == 200:
                item = Item()
                populate_instance(item, res.json())
                db.session.add(item)
            else:
                raise Exception
        db.session.commit()   # commit all data at once
        print("Done fetching")
    except Exception:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()


def initialize_databse():
    with app.app_context():
        # To make sure this only runs when databse is empty
        if Item.query.first() is not None:
            return
        else:
            max = fetch_max()
            if max is not None:
                fetch_data(max-99, max+1)
            else:
                return


def update_database():
    try:
        r = requests.get(update_url)
        if r.status_code == 200:
            response = r.json()
        else:
            raise Exception

        updates = response.get('items', [])
        print(updates)
        for id in updates:
            item = Item.query.filter(Item.hacker_news_id == id).first()
            if item is None:   # Not present id out database
                continue

            r = requests.get(item_url.format(id))
            if r.status_code == 200:
                populate_instance(item, r.json())
                db.session.add(item)
            else:
                raise ConnectionError
        db.session.commit()
        print("Database up to date")
    except Exception:
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()


def sync_database():
    app = scheduler.app
    with app.app_context():
        try:
            print("Synchronizing database server with hacker news...")
            item = Item.query.order_by(db.desc(Item.hacker_news_id)).first()
            prev_maxid = item.hacker_news_id
            print(prev_maxid)
            new_maxid = fetch_max()
            if new_maxid is None:
                print("Connection Error")
                return
            print(new_maxid)
            fetch_data(prev_maxid + 1, new_maxid + 1)
            update_database()
        except KeyboardInterrupt:
            scheduler.shutdown()
            sys.exit(1)


initialize_databse()

scheduler.add_job(id='sync_database', func=sync_database, trigger='interval',
            minutes=5, max_instances=1)
scheduler.start()

# -------------------------------------------------------------------#
# Routes.
# -------------------------------------------------------------------#


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        filter = request.args.get('filter')
    else:
        filter = request.form.get('filter')
    try:
        if filter is not None:
            items = Item.query.filter(Item.type == filter).\
                filter(Item.dead == None).filter(Item.deleted == None).\
                order_by(db.desc(Item.time_posted)).all()
        else:
            items = Item.query.filter(Item.type != 'comment').\
                filter(Item.type != 'pollopt').filter(Item.dead == None).\
                filter(Item.deleted == None).\
                order_by(db.desc(Item.time_posted)).all()
        page = request.args.get('page', 1, type=int)
        if page < 1:
            abort(404)
        data = paginate_news(page, items)
        data['filter'] = filter
    except Exception:
        print(sys.exc_info())
        abort(500)

    return render_template('pages/index.html', data=data)


@app.route('/news/<int:item_id>', methods=['GET'])
def get_detail(item_id):
    not_found = False
    try:
        item = Item.query.filter(Item.id == item_id).first()

        if item is None:
            not_found = True
            raise NotFound

        # Check for item type and return appropriate sub item
        if item.type != 'poll':
            sub_items = Item.query.filter(Item.type == 'comment').\
                filter(Item.parent == item_id).all()
        else:
            sub_items = Item.query.filter(Item.type == 'pollopt').\
                filter(Item.parent == item_id).all()
    except Exception:
        print(sys.exc_info())
        if not_found:
            abort(404)
        abort(500)

    return render_template('pages/detail.html', news=item, sub_items=sub_items)


@app.route('/search', methods=['GET', 'POST'])
def search_news():
    if request.method == 'POST':
        search_term = request.form.get('search_term', '')
    else:
        search_term = request.args.get('search_term', '')
    try:
        items = Item.query.filter(Item.title.ilike('%'+search_term+'%')).\
            all()
        page = request.args.get('page', 1, type=int)
        data = paginate_news(page, items)
        data['count'] = len(items)
        data['search_term'] = search_term
    except Exception:
        print(sys.exc_info())
        abort(500)

    return render_template('pages/search.html', data=data)

# ---------------------------------------------------------------------#
# API Endpoints
# ---------------------------------------------------------------------#


@app.route('/api/v1/items', methods=['GET'])
def get_items():
    filter = request.args.get('filter', '', str)
    page = request.args.get('page', 1, int)
    try:
        if filter == '':
            items = Item.query.all()
        else:
            items = Item.query.filter(Item.type == filter).\
                order_by(db.desc(Item.time_posted)).all()
        data = paginate_news(page, items, 100)
        result = data['news']
    except Exception:
        print(sys.exc_info())
        abort(500)

    return (jsonify({'items': result}), 200)


@app.route('/api/v1/item/<int:item_id>', methods=['GET'])
def get_item(item_id):
    not_found = True
    try:
        item = Item.query.filter(Item.id == item_id).first()

        if item is None:
            not_found = True
            raise NotFound
    except Exception:
        print(sys.exc_info())
        if not_found:
            abort(404)
        abort(500)

    return (jsonify(item.format()), 200)


@app.route('/api/v1/item', methods=['POST'])
def create_item():
    # Abort if title is null
    if request.form.get('title') is not None:
        try:
            # Query database to check if item exists and is from HN
            item = Item.query.\
                filter(Item.title == request.form.get('title')).\
                filter(Item.hacker_news_id != None).first()
            if item is None:                    # Item doesn't exist
                item = Item()
                populate_instance(item, request.form)
            else:
                abort(422)
            db.session.add(item)
            db.session.commit()
            response = {
                'success': True,
                'id': item.id,
            }
        except Exception:
            print(sys.exc_info())
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()
    else:
        abort(422)

    return jsonify(response), 201


@app.route('/api/v1/item/<int:item_id>', methods=['PATCH'])
def update_item(item_id):
    not_found = False
    item = Item.query.filter(Item.id == item_id).\
        filter(Item.hacker_news_id != None).first()
    if item is not None:     # Item belongs to Hacker News
        abort(422)
    try:
        item = Item.query.filter(Item.id == item_id).one_or_none()

        if item is None:
            not_found = True
            raise NotFound

        populate_instance(item, request.form)
        db.session.commit()
        response = {
            'success': True,
            'id': item.id
        }
    except Exception:
        print(sys.exc_info())
        db.session.rollback()
        if not_found:
            abort(404)
        abort(500)
    finally:
        db.session.close()

    return jsonify(response), 200


@app.route('/api/v1/item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    not_found = False
    item = Item.query.filter(Item.id == item_id).\
        filter(Item.hacker_news_id != None).first()
    if item is not None:     # Item belongs to Hacker News
        abort(422)
    try:
        item = Item.query.filter(Item.id == item_id).first()

        if item is None:
            not_found = True
            raise NotFound

        db.session.delete(item)
        db.session.commit()
    except Exception:
        print(sys.exc_info())
        db.session.rollback()
        if not_found:
            abort(422)
        abort(500)
    finally:
        db.session.close()

    return jsonify(
        {
            'success': True,
            'id': item_id
        }
    ), 200


# ------------------------------------------------------------------#
# Error handlers.
# ------------------------------------------------------------------#


@app.errorhandler(400)
def bad_request(error):
    return (
        jsonify(
            {
                "success": False,
                "error": 400,
                "message": "bad request"
            }), 400
        )


@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api'):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                }), 404
            )
    return render_template('/errors/404.html')


@app.errorhandler(422)
def unprocessable(error):
    return (
        jsonify(
            {
                "success": False,
                "error": 422,
                "message": "unprocessable"
            }), 422
        )


@app.errorhandler(405)
def not_allowed(error):
    return (
        jsonify(
            {
                "success": False,
                "error": 405,
                "message": "method not allowed"
            }), 405
        )


@app.errorhandler(500)
def bad_request(error):
    if request.path.startswith('/api'):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 500,
                    "message": "internal server error"
                }), 500
            )
    return render_template('/errors/500.html')


# ----------------------------------------------------------------#
# Logging
# -----------------------------------------------------------------#


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s \
        [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#
# Default port:


if __name__ == '__main__':
    app.run()
