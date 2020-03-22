import subprocess,os
import time
import json

gtusername = 'gburdell3' # TODO: Replace your gtusername here

def login(proc, username, user_key):
    proc.stdin.write(username + '\n')
    proc.stdin.write(user_key + '\n')

def checkin(proc, document_name, security_flag):
    proc.stdin.write('1\n')
    proc.stdin.write(document_name + '\n')
    proc.stdin.write(security_flag + '\n')

def checkout(proc, document_name):
    proc.stdin.write('2\n')
    proc.stdin.write(document_name + '\n')

def grant(proc, document_name, target_user, access_right, time_duration):
    proc.stdin.write('3\n')
    proc.stdin.write(document_name + '\n')
    proc.stdin.write(target_user + '\n')
    proc.stdin.write(access_right + '\n')
    proc.stdin.write(time_duration + '\n')

def delete(proc, document_name):
    proc.stdin.write('4\n')
    proc.stdin.write(document_name + '\n')

def logout(proc):
    proc.communicate('5\n')

def check_testresult(test_number):
    time.sleep(0.5)
    try:
        with open('../client1/'+gtusername,'r+') as f:
            output =  f.read()
            f.truncate(0)
            if output and str(json.loads(output)['status']) == '200':
                print "Test Case " +  str(test_number) + " - Passed"
            else:
                print "Test Case " + str(test_number) + " - Failed"
    except:
        print "Testing aborted due to failure!"
        exit(1)


def main():
    FNULL = open(os.devnull, 'w')
    try:
        p = subprocess.Popen(
            ['./start_server.sh'],
            cwd ='../server/application',
            stdout=FNULL,
            stderr=FNULL,
        )
        time.sleep(1)
    except:
        print "Failed to start the server! Aborting!"
        exit(1)

    try:
        proc = subprocess.Popen(
            ['python', 'client.py'],
            cwd ='../client1',
            stdin=subprocess.PIPE,
            stdout=FNULL,
            stderr=FNULL,
        )
    except:
        print "Failed to invoke the client! Aborting!"
        exit(1)

    # Login
    username = '' # TODO: Place username
    user_key = '' # TODO: Place user private key file name present inside userkeys folder
    login(proc, username, user_key)
    check_testresult(1)

    # Checkin
    document_name = 'test_document' # TODO: Can be replaced with any document name
    security_flag = '1' # confidentiality
    try:
        with open('../client1/documents/checkin/'+document_name,'w') as f:
            f.write('Test input for checkin')
    except:
        print "Failed to write checkin file! Exiting"
    checkin(proc, document_name, security_flag)
    check_testresult(2)

    # Checkout
    checkout(proc, document_name)
    check_testresult(3)

    # Grant
    target_user = '' # TODO: Place the target username
    access_right = '1' # checkin
    time_duration = '10'
    grant(proc, document_name, target_user, access_right, time_duration)
    check_testresult(4)

    # Delete
    delete(proc, document_name)
    check_testresult(5)

    # Logout
    logout(proc)
    check_testresult(6)


if __name__ == '__main__':
    main()
