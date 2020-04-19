from flask import Flask, request, jsonify
from flask_restful import Resource, Api

from middleware import middleware

import os
import io
import jwt
import base64
from datetime import datetime

import Crypto.Hash.MD5 as MD5
from Crypto.PublicKey import RSA


secure_shared_service = Flask(__name__)
api = Api(secure_shared_service)

JWT_ALGORITHM = 'HS256'
API_KEY = 'uytv3a0p84dh9xs2gj3n9xlnbcimrllx'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_KEY_DIR = os.path.join(BASE_DIR, 'userpublickeys')
DOCUMENTS_DIR = os.path.join(BASE_DIR, 'documents')


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

        with io.open(public_key_path, 'r', encoding='utf-8') as public_key_file:
            public_key_content = public_key_file.read()
            public_key = RSA.importKey(public_key_content)

        return public_key


    def post(self):
        data = request.get_json()

        user_id = data['user_id']
        statement = data['statement']
        signed_statement = data['signed_statement']

        public_key = self._get_public_key(user_id)

        hash_ = MD5.new(statement).digest()
        success = public_key.verify(hash_, signed_statement)

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

    def post(self):
        data = request.get_json()

        document_id = data['document_id']
        document = os.path.join(DOCUMENTS_DIR, document_id)

        response = {
            'status': 200,
            'message': 'Document Successfully checked out',
        }


        with open(document, 'rb') as binary_file:
            response['binary_file'] = base64.b64encode(binary_file.read())


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

    def post(self):
        data = request.get_json()

        document_id = data['document_id']
        security_flag = data['security_flag']
        binary_file = data['binary_file']

        file_ = base64.b64decode(binary_file)
        with open(os.path.join(DOCUMENTS_DIR, document_id), 'wb') as output_file:
            output_file.write(file_)

        # TODO: Implement checkin functionality
        '''
            Expected response status codes:
            1) 200 - Document Successfully checked in
            2) 702 - Access denied to check in
            3) 700 - Other failures
        '''

        response = {
            'status': 200,
            'message': 'Document Successfully checked in',
        }

        return jsonify(response)


class grant(Resource):

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

    def post(self):
        data = request.get_json()

        document_id = data['document_id']
        document = os.path.join(DOCUMENTS_DIR, document_id)


        status = 700
        message = 'Other failures'


        try:
            if False:
                status = 702
                message = 'Access denied to delete file'

            else:
                os.remove(document)

                status = 200
                message = 'Successfully deleted the file'

        except OSError as e:

            if e.errno == errno.ENOENT:
                status = 704
                message = 'Delete failed since file not found on the server'


        response = {
            'status': status,
            'message': message,
        }

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

        response = {
            'status': 200,
            'message': 'Logout Successful',
        }

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
