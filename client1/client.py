import os
import glob
import json
import requests
import shutil


import Crypto.Hash.MD5 as MD5
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHECK_OUT_DIR = os.path.join(BASE_DIR, 'documents', 'checkout')
CHECK_IN_DIR = os.path.join(BASE_DIR, 'documents', 'checkin')


client_name = os.path.basename(BASE_DIR)
gt_username = 'agarcia327'
#TODO: Change back
#server_name = 'secure-shared-store'
server_name = 'http://localhost:5000'
node_certificate = 'certs/%s.crt' % client_name
node_key = 'certs/%s.key' % client_name
session_token = None


''' <!!! DO NOT MODIFY THIS FUNCTION !!!>'''
def post_request(server_name, action, body, node_certificate, node_key):
    '''
    node_certificate is the name of the certificate file of the client node (present inside certs).
    node_key is the name of the private key of the client node (present inside certs).
    body parameter should in the json format.
    '''

#TODO: Change back
    #request_url= 'https://{}/{}'.format(server_name,action)
    request_url= '{}/{}'.format(server_name, action)
    request_headers = {
        'Content-Type': "application/json"
    }

    response = requests.post(
        url=request_url,
        data=json.dumps(body),
        headers=request_headers,
        cert=(node_certificate, node_key),
    )

    with open(gt_username, 'w') as f:
        f.write(response.content)

    return response


def _sign_statement(private_key_path, message):
    private_key = None

    with open(private_key_path, 'r', encoding='utf-8') as private_key_file:
        private_key_content = private_key_file.read()
        private_key = RSA.importKey(private_key_content)

    cipher_rsa = PKCS1_OAEP.new(private_key)
    encoded_message = message.encode()
    signed_message = cipher_rsa.encrypt(encoded_message)

    return signed_message


def _clear_files():
    checkin_files = glob.glob(CHECK_IN_DIR)
    checkout_files = glob.glob(CHECK_OUT_DIR)

    files = checkin_files + checkout_files
    for file_ in files:
        os.remove(file_)


def login(user_id, private_key_path):

    statement = '%s as %s logs into the Server' % (client_name, user_id)

    signed_statement = _sign_statement(private_key_path, statement)
    signed_statement = signed_statement.decode('utf-8', 'backslashreplace')

    body = {
        'user_id': user_id,
        'statement': statement,
        'signed_statement': signed_statement,
    }

    response = post_request(
        server_name=server_name,
        action='login',
        body=body,
        node_certificate=node_certificate,
        node_key=node_key,
    )

    session_token = response['session_token']
    if session_token:
        _clear_files()

    return response


def checkin(document_id, security_flag):

    checked_out_file = os.path.join(CHECK_OUT_DIR, document_id)
    checked_in_file = os.path.join(CHECK_IN_DIR, document_id)

    if os.path.isfile(checked_out_file):
        shutil.move(checked_out_file, checked_in_file)

    body = {
        'document_id': document_id,
        'security_flag': security_flag,
        'session_token': session_token,
    }

    with open(checked_in_file, 'rb') as binary_file:
        body['binary_file'] = binary_file

    response = post_request(
        server_name=server_name,
        action='checkin',
        body=body,
        node_certificate=node_certificate,
        node_key=node_key,
    )

    return response


def checkout(document_id):

    body = {
        'document_id': document_id,
        'session_token': session_token,
    }

    response = post_request(
        server_name=server_name,
        action='checkout',
        body=body,
        node_certificate=node_certificate,
        node_key=node_key,
    )

    output_path = os.path.join(BASE_DIR, 'documents', 'checkout', document_id)
    with open(output_path, 'wb') as document:
        binary_file = response.content['document']
        document.write(binary_file)

    return response


def grant(document_id, target_user, access, duration):

    body = {
        'document_id': document_id,
        'target_user': target_user,
        'access': access,
        'duration': duration,
        'session_token': session_token,
    }

    response = post_request(
        server_name=server_name,
        action='grant',
        body=body,
        node_certificate=node_certificate,
        node_key=node_key,
    )

    return response


def delete(document_id):

    body = {
        'document_id': document_id,
        'session_token': session_token,
    }

    response = post_request(
        server_name=server_name,
        action='delete',
        body=body,
        node_certificate=node_certificate,
        node_key=node_key,
    )

    return response


def logout():

    checked_out_documents = os.listdir(CHECK_OUT_DIR)
    for document_id in checked_out_documents:
        checkin(document_id, 2)

    body = {
        'session_token': session_token,
    }

    response = post_request(
        server_name=server_name,
        action='logout',
        body=body,
        node_certificate=node_certificate,
        node_key=node_key,
    )

    exit()


def main():
    '''
        # TODO: Authenticate the user by calling login.
            If the login is successful, provide the following options to the user
            1. Checkin
            2. Checkout
            3. Grant
            4. Delete
            5. Logout
            The options will be the indexes as shown above. For example, if user
            enters 1, it must invoke the Checkin function. Appropriate functions
            should be invoked depending on the user input. Users should be able to
            perform these actions in a loop until they logout. This mapping should
            be maintained in your implementation for the options.
    '''
    user_id = 'user1'
    private_key_path = 'userkeys/user1.key'

    login(user_id, private_key_path)


if __name__ == '__main__':
    main()


