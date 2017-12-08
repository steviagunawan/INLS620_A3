from flask import (Flask, Response, request, render_template, make_response,
                   redirect)
from flask_restful import Api, Resource, reqparse, abort

import json
import random
import string
from datetime import datetime
from functools import wraps

with open('all_reviews.json') as data:
    data = json.load(data)

def generate_id(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def error_if_review_not_found(review_id):
    if review_id not in data['reviews']:
        message = "No review with ID: {}".format(review_id)
        abort(404, message=message)

#
def render_review_list_as_html(reviews):
    return render_template(
        'reviewList.html',
        reviews=reviews)
#
def render_review_as_html(review):
    return render_template(
        'review.html',
        review = review)

def nonempty_string(x):
    s = str(x)
    if len(x) == 0:
        raise ValueError('string is empty')
    return s


# Specify the data necessary to create a new help ticket.
# "from", "title", and "description" are all required values.
new_reviewList_parser = reqparse.RequestParser()
for arg in ['username', 'review']:
    new_reviewList_parser.add_argument(
        arg, type=nonempty_string, required=True,
        help="'{}' is a required value".format(arg))

update_review_parser = reqparse.RequestParser()
update_review_parser.add_argument(
    'text', type=str, default='')

class ReviewList(Resource):

    def get(self):
        return make_response(render_template('reviewList.html', reviews=data['reviews']),200)

    def post(self):
        reviews = new_reviewList_parser.parse_args()
        review_id = generate_id()
        # reviews['@id'] = 'reviewid/' + review_id
        reviews['review_name'] = 'review' + review_id
        reviews['game_name'] = 'Game 1'
        reviews['date'] = datetime.isoformat(datetime.now())
        data['reviews'][review_id] = reviews
        return make_response(
            render_template(
                'reviewList.html', reviews=data['reviews']), 201)


class Review(Resource):

    def get(self,review_id):
        error_if_review_not_found(review_id)
        return make_response(render_template('review.html',reviews=data['reviews'][review_id]),200)

    def patch(self, review_id):
        error_if_review_not_found(review_id)
        review = data['reviews'][review_id]
        update = update_review_parser.parse_args()
        if len(update['text'].strip()) > 0:
            review.setdefault('texts', []).append(update['text'])
        return make_response(render_review_as_html(review), 200)


app = Flask(__name__)
api = Api(app)
api.add_resource(ReviewList, '/reviews')
api.add_resource(Review, '/reviews/<string:review_id>')


@app.route('/')
def index():
    return redirect(api.url_for(ReviewList), code=303)

@app.after_request
def after_request(response):
    response.headers.add(
        'Access-Control-Allow-Origin', '*')
    response.headers.add(
        'Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add(
        'Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5555,
        debug=True,
        use_debugger=False,
        use_reloader=False)
