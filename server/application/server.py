from flask import Flask, request, jsonify
from flask_restful import Resource, Api

from middleware import middleware

import os
import io
import jwt
import base64
from datetime import datetime
from enum import Enum

import Crypto.Hash.MD5 as MD5
from Crypto.PublicKey import RSA


secure_shared_service = Flask(__name__)
api = Api(secure_shared_service)

JWT_ALGORITHM = 'HS256'
API_KEY = 'uytv3a0p84dh9xs2gj3n9xlnbcimrllx'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_KEY_DIR = os.path.join(BASE_DIR, 'userpublickeys')

SERVER_DIR = os.path.dirname(BASE_DIR)
SERVER_PRIVATE_KEY = os.path.join(SERVER_DIR, 'certs', 'secure-shared-store.key')
SERVER_PUBLIC_KEY = os.path.join(SERVER_DIR, 'certs', 'secure-shared-store.pub')

DOCUMENTS_DIR = os.path.join(BASE_DIR, 'documents')
SIGNED_DOCUMENTS_DIR = os.path.join(BASE_DIR, 'signed_documents')



class SecurityFlag(Enum):
    Confidentiality = 1
    Integrity = 2


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

    def _verify(self, document_id, document):
        verified = False
        public_key = None

        with io.open(SERVER_PUBLIC_KEY, 'r', encoding='utf-8') as public_key_file:
            public_key_content = public_key_file.read()
            public_key = RSA.importKey(public_key_content)

        signed_document = os.path.join(SIGNED_DOCUMENTS_DIR, document_id)
        with io.open(signed_document, 'rb') as binary_file:
            signed_data = binary_file.read()
            signed_data = (long(signed_data), )

            hash_ = MD5.new(document).digest()
            verified = public_key.verify(hash_, signed_data)


        return verified


    def post(self):
        data = request.get_json()

        document_id = data['document_id']
        document = os.path.join(DOCUMENTS_DIR, document_id)

        response = {
            'status': 200,
            'message': 'Document Successfully checked out',
        }


        with open(document, 'rb') as binary_file:
            data = binary_file.read()
            verified = self._verify(document_id, data)

            response['document'] = base64.b64encode(data)


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

    def _encrypt(self, document):
        return document


    def _sign(self, document_id, document):
        private_key = None

        with io.open(SERVER_PRIVATE_KEY, 'r', encoding='utf-8') as private_key_file:
            private_key_content = private_key_file.read()
            private_key = RSA.importKey(private_key_content)

        hash_ = MD5.new(document).digest()
        signed_document = private_key.sign(hash_, '')

        with open(os.path.join(SIGNED_DOCUMENTS_DIR, document_id), 'wb') as output_file:
            signed_document = str(signed_document[0])
            output_file.write(signed_document)


    def post(self):
        data = request.get_json()

        document_id = data['document_id']
        binary_file = data['binary_file']

        value = data['security_flag']
        security_flag = SecurityFlag(value)


        document = base64.b64decode(binary_file)
        with open(os.path.join(DOCUMENTS_DIR, document_id), 'wb') as output_file:

            if security_flag == SecurityFlag.Confidentiality:
                document = self._encrypt(document)
            elif security_flag == SecurityFlag.Integrity:
                self._sign(document_id, document)

            output_file.write(document)

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
        signed_document = os.path.join(SIGNED_DOCUMENTS_DIR, document_id)


        status = 700
        message = 'Other failures'


        try:
            os.remove(signed_document)
        except Exception as e:
            pass


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

    try:
        os.makedirs(DOCUMENTS_DIR)
        os.makedirs(SIGNED_DOCUMENTS_DIR)
    except Exception as e:
        pass

    secure_shared_service.run(debug=True)


if __name__ == '__main__':
	main()
