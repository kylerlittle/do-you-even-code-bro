import configparser
from utils.file_utils import get_absolute_path
from github import Github
import subprocess
import pathlib

relative_path_from_utils_dir = '../../../.config/config.ini'
config = configparser.ConfigParser()
config.read(get_absolute_path(relative_path_from_utils_dir))

def get_github_credentials():
    return (config['GITHUB_CREDENTIALS']['USERNAME'], config['GITHUB_CREDENTIALS']['PASSWORD'])

def clone_repo(clone_url):
    try:
        # Only clone most recent version
        args = ['git', 'clone', '--depth', '1', clone_url]
        subprocess.check_call(args)
    except subprocess.CalledProcessError as cpe:
        print(cpe.__cause__)

def delete_repo(repo_name):
    try: 
        args = ['rm', '-rf', repo_name]
        subprocess.check_call(args)
    except subprocess.CalledProcessError as cpe:
        print(cpe.__cause__)

def count_lines_of_code(dir):
    try:
        args = ['cloc', dir]
        subprocess.check_call(args)
    except subprocess.CalledProcessError as cpe:
        print (cpe.__cause__)

def count_lines_of_code_to_sqlite(project_name, dir, db_name):
    try:
        args = ['cloc', '--sql', '1', '--sql-project', project_name, dir]
        if pathlib.Path(db_name).exists(): 
            args.insert(args.index(dir), '--sql-append')
        proc1 = subprocess.Popen(args, stdout=subprocess.PIPE)
        proc2 = subprocess.Popen(['sqlite3', db_name], stdin=proc1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc1.stdout.close()
        proc2.communicate()
    except subprocess.CalledProcessError as cpe:
        print(cpe.__cause__)
        

def main():
    _user, _pass = get_github_credentials()
    github_client = Github(_user, _pass)
    db_name = config['SQLITE']['DBFILE']
    repo_list = github_client.get_user().get_repos()
    for repo in repo_list:
        if repo.name != 'hackmit_2017':
            clone_repo(repo.clone_url)
            count_lines_of_code_to_sqlite(repo.name, repo.name, db_name)
            delete_repo(repo.name)

if __name__ == '__main__':
    main()
