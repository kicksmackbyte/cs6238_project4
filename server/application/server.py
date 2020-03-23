from flask import Flask, request, jsonify
from flask_restful import Resource, Api

from middleware import middleware

from functools import wraps


secure_shared_service = Flask(__name__)
api = Api(secure_shared_service)


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

    def post(self):
        data = request.get_json()

        # TODO: Implement login functionality
        '''
            # TODO: Verify the signed statement.
            Response format for success and failure are given below. The same
            keys ('status', 'message', 'session_token') should be used.
        '''
        if success:
            session_token = '' # TODO: Generate session token
            # Similar response format given below can be used for all the other functions
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
