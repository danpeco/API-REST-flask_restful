from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource, abort, reqparse

from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

import datetime

from books import BOOKS
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

api = Api(app)

jwt = JWTManager(app)

book_parser = reqparse.RequestParser()
# help value: what to display to sender if he don't send needed arguments
book_parser.add_argument('isbn', type=str)
book_parser.add_argument('title', type=str, help='title of the book required', required=True)
book_parser.add_argument('description', type=str)
book_parser.add_argument('author', type=str, help='author of the book required', required=True)


@app.route('/login', methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username != "test" or password != "test":
        return jsonify({"message": "Bad username or password"}), 401

    access_token = create_access_token(identity=username, expires_delta=datetime.timedelta(minutes=5))
    return jsonify(access_token=access_token)


def abort_if_book_doesnt_exist(book_id):
    if book_id not in BOOKS:
        abort(404, message=f'The book with the id {book_id} does not exist')


class BookList(Resource):

    def get(self):
        return make_response(jsonify({'Books data': BOOKS}), 200)

    @jwt_required()
    def post(self):
        args = book_parser.parse_args()
        BOOKS[max(BOOKS.keys()) + 1] = args
        return make_response(jsonify({'message': 'Product added succesfully', 'Books data': BOOKS}), 201)   #201


class Book(Resource):
    def get(self, book_id):
        abort_if_book_doesnt_exist(book_id)
        return make_response(jsonify({'Books data': BOOKS[book_id]}), 200)

    @jwt_required()
    def put(self, book_id):
        abort_if_book_doesnt_exist(book_id)
        args = book_parser.parse_args()
        BOOKS[book_id] = args
        return make_response(jsonify({'message': f'Product id:{book_id} updated', 'Books data': BOOKS}), 200)

    @jwt_required()
    def delete(self, book_id):
        abort_if_book_doesnt_exist(book_id)
        del BOOKS[book_id]
        return make_response(jsonify({'message': f'Product id:{book_id} deleted', 'Books data': BOOKS}), 204)   #204


api.add_resource(BookList, '/books')
api.add_resource(Book, '/books/<int:book_id>')


if __name__ == '__main__':
    app.run(debug=True)