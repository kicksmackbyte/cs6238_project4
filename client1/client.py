import os
import requests


import Crypto.Hash.MD5 as MD5

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


gt_username = 'agarcia327'   # TODO: Replace with your gt username within quotes
server_name = 'secure-shared-store'
node_certificate = 'certs/CA.crt'
node_key = 'certs/CA.key'


''' <!!! DO NOT MODIFY THIS FUNCTION !!!>'''
def post_request(server_name, action, body, node_certificate, node_key):
    '''
    node_certificate is the name of the certificate file of the client node (present inside certs).
    node_key is the name of the private key of the client node (present inside certs).
    body parameter should in the json format.
    '''

    request_url= 'https://{}/{}'.format(server_name,action)
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


class PrivateKey(object):

    def __init__(self, filename):
        with open(filename, 'r') as private_key_file:
            self.key = private_key_file

        os.remove(filename)


    def sign(message):
        hashed_message = MD5.new(message).digest()
        signed_message = self.key.sign(hashed_message)

        return signed_message


def login(user_id, filename):

    statement = 'Client%s as User%s logs into the Server' % (1, user_id)

    private_key = PrivateKey(filename)
    signed_statement = private_key.sign(statement)

    body = {
        'user-id': user_id,
        'statement': statement,
        'signed-statement': signed_statement,
    }

    response = post_request(
        server_name=server_name,
        action='login',
        body=body,
        node_certificate=node_certificate,
        node_key=node_key,
    )

    return response


def checkin(document_id, security_flag):

    #TODO: if document_id exists in checkout folder must move to checkin folder

    body = {
        'document_id': document_id,
        'security_flag': security_flag,
    }

    with open(document_id, 'rb') as binary_file:
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
    }

    response = post_request(
        server_name=server_name,
        action='checkout',
        body=body,
        node_certificate=node_certificate,
        node_key=node_key,
    )

    output_path = os.path.join(BASE_DIR, 'documents', 'checkin', document_id)
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

    checked_out_documents = [] #TODO: Read documents/checkedout directory
    for document_id in checked_out_documents:
        checkin(document_id, 2)

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


if __name__ == '__main__':
    main()


