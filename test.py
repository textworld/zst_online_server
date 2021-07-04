from git import Repo
import os
import sys
import git

if __name__ == '__main__':
    p = '/tmp/mysql_playbook'

    if not os.path.exists(p):
        os.mkdir(p)
        Repo.clone_from('git@github.com:textworld/ansible_zst_mysql.git', p)

    if not os.path.isdir(p):
        print("is not dir")
        sys.exit(1)

    repo = Repo(p)

    repo.remote("origin").pull()

