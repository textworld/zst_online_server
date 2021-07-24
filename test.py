from git import Repo
import os
import sys
import git
import re

if __name__ == '__main__':

    t = 'user: zst gender: g3d age: 18'
    pattern = re.compile(r'(username|user): (?P<name>[a-zA-Z0-9._-]+) gender: (?P<gender>[a-zA-Z0-9._-]+) age: (?P<age>\w+)')
    m = pattern.match(t)
    if m is None:
        print("match failed")
    else:
        print("match success")
        d = m.groupdict()
        print("username", d['name'])



    # p = '/tmp/mysql_playbook'
    #
    # if not os.path.exists(p):
    #     os.mkdir(p)
    #     Repo.clone_from('git@github.com:textworld/ansible_zst_mysql.git', p)
    #
    # if not os.path.isdir(p):
    #     print("is not dir")
    #     sys.exit(1)
    #
    # repo = Repo(p)
    #
    # repo.remote("origin").pull()

