from flask import Flask, request, jsonify
from flask_restful import Resource, Api

from middleware import middleware

import os
import base64
from functools import wraps
from datetime import datetime

import Crypto.Hash.MD5 as MD5
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


secure_shared_service = Flask(__name__)
api = Api(secure_shared_service)

JWT_ALGORITHM = 'HS256'
API_KEY = 'uytv3a0p84dh9xs2gj3n9xlnbcimrllx'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_KEY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'application', 'userpublickeys')


def check_permission(permission):
    @wraps(permission)
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal permission

            auth_header = request.headers.get('Authorization')
            if auth_header:
                try:
                    auth_token = auth_header.split(' ')[1]
                except IndexError:
                    response = {
                            'status': 'fail',
                            'message': 'Bearer token malformed',
                        }

                    return response
            else:
                auth_token = None

            if auth_token:
                token_data = jwt.decode(auth_token)
                access = token_data.get(permission)

                if not access:
                    raise Exception('not authorized')

            return func(*args, **kwargs)

        return wrapper
    return decorator


class welcome(Resource):

    def get(self):
        return "Welcome to the secure shared server!"


class login(Resource):

    def __generate_session_token(self, user_id):

        timestamp = datetime.utcnow()

        payload = {
                    'user_id': user_id,
                    'iat': timestamp,
                }

        encoded_jwt = jwt.encode(payload, API_KEY, algorithm=JWT_ALGORITHM).decode('utf-8')

        return encoded_jwt


    def _get_public_key(self, user_id):
        public_key_path = os.path.join(PUBLIC_KEY_DIR, user_id+'.pub')

        with open(public_key_path, 'r', encoding='utf-8') as public_key_file:
            public_key_content = public_key_file.read()
            public_key = RSA.importKey(public_key_content)
            cipher_rsa = PKCS1_OAEP.new(public_key)

        return cipher_rsa


    def post(self):
        data = request.get_json()

        user_id = data['user_id']
        statement = data['statement']
        signed_statement = data['signed_statement']

        public_key = self._get_public_key(user_id)

        signed_statement = signed_statement.encode()
        signed_statement = signed_statement.decode('utf-8', 'backslashreplace')
        signed_statement = base64.b64decode(signed_statement)

        decrypted_statement = public_key.decrypt(signed_statement)
        success = statement == decrypted_statement

        if success:
            session_token = self.__generate_session_token(user_id)

            response = {
                'status': 200,
                'message': 'Login Successful',
                'session_token': session_token,
            }
        else:
            response = {
                'status': 700,
                'message': 'Login Failed'
            }

        return jsonify(response)


class checkout(Resource):
    method_decorators = [check_permission('checkout')]

    def post(self):
        data = request.get_json()

        # TODO: Implement checkout functionality
        '''
            Expected response status codes
            1) 200 - Document Successfully checked out
            2) 702 - Access denied to check out
            3) 703 - Check out failed due to broken integrity
            4) 704 - Check out failed since file not found on the server
            5) 700 - Other failures
        '''

        return jsonify(response)


class checkin(Resource):
    method_decorators = [check_permission('checkin')]

    def post(self):
        data = request.get_json()

        # TODO: Implement checkin functionality
        '''
            Expected response status codes:
            1) 200 - Document Successfully checked in
            2) 702 - Access denied to check in
            3) 700 - Other failures
        '''

        return jsonify(response)


class grant(Resource):
    method_decorators = [check_permission('grant')]

    def post(self):
        data = request.get_json()

        # TODO: Implement grant functionality
        '''
            Expected response status codes:
            1) 200 - Successfully granted access
            2) 702 - Access denied to grant access
            3) 700 - Other failures
        '''

        return jsonify(response)


class delete(Resource):
    method_decorators = [check_permission('delete')]

    def post(self):
        data = request.get_json()

        # TODO: Implement delete functionality
        '''
            Expected response status codes:
            1) 200 - Successfully deleted the file
            2) 702 - Access denied to delete file
            3) 704 - Delete failed since file not found on the server
            4) 700 - Other failures
        '''

        return jsonify(response)


class logout(Resource):
    def post(self):
        data = request.get_json()

        # TODO: Implement logout functionality
        '''
            Expected response status codes:
            1) 200 - Successfully logged out
            2) 700 - Failed to log out
        '''

        return jsonify(response)


api.add_resource(welcome, '/')
api.add_resource(login, '/login')
api.add_resource(checkin, '/checkin')
api.add_resource(checkout, '/checkout')
api.add_resource(grant, '/grant')
api.add_resource(delete, '/delete')
api.add_resource(logout, '/logout')


def main():
	secure_shared_service.run(debug=True)


if __name__ == '__main__':
	main()
