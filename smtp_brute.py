#!/usr/bin/python3
"""
Usage:
  smtp_verify.py -h | --help
  smtp_verify.py (--rhosts=<rhosts> --users=<users>)
 
Options:
  --rhosts=<rhosts> Single ip per line
  --users=<users>   Single user per line
"""

import json
import socket
import concurrent.futures
from docopt import docopt


def gen_user_list(users):
    users_list = []
    with open(users, "r") as file:
        for user in file:
            users_list.append(user.strip("\n"))
    return users_list

def gen_rhost_list(rhosts):
    rhosts_list = []
    with open(rhosts, "r") as file:
        for host in file:
            rhosts_list.append(host.strip("\n"))
    return rhosts_list

def send_verify(user, ip):
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    print("testing user {} on ip {}".format(user, ip))
    try:
        connect=s.connect((ip,25))
        banner=s.recv(1024)
        data = b'VRFY ' + user.encode() + b'\r\n' 
        s.send(data)
        result = s.recv(1024)
        print("successful connection to ip {} for user {}".format(ip, user))
        return user
        s.close()
    except Exception:
        return False

def send_verify_concurrent_users(ip, users):
    results = {ip:[]}
    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as pool:
        results = {pool.submit(send_verify, user, ip): user for user in users}
        for future in concurrent.futures.as_completed(results):
            if future.result():
                results['ip'].append(future.result())
    return results

def send_verify_concurrent(rhosts, users):
    results_list = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as pool:
        results = {pool.submit(send_verify_concurrent_users, str(ip), users): ip for ip in rhosts}
        for future in concurrent.futures.as_completed(results):
            if future.result():
                results_list.append(future.result())
    print(results_list)
    return results_list

def write_log(data, filename="smtp_enum.log"):
    with open(filename, "w+") as file:
        file.write(json.dumps(data, indent=4))

def main():
    opts = docopt(__doc__)
    rhosts = gen_rhost_list(opts['--rhosts'])
    users = gen_user_list(opts['--users'])
    res = send_verify_concurrent(
        rhosts=rhosts,
        users=users
    )
    print(res)
    write_log(res)

if __name__ == '__main__':
    main()
