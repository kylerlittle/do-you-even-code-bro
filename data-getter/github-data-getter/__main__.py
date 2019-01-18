import configparser
from utils.file_utils import get_absolute_path
from github import Github
import subprocess
import pathlib
import os
import psycopg2
import re

relative_path_from_utils_dir = '../../../.config/config.ini'
config = configparser.ConfigParser()
config.read(get_absolute_path(relative_path_from_utils_dir))

def get_github_credentials():
    return (config['GITHUB_CREDENTIALS']['USERNAME'], config['GITHUB_CREDENTIALS']['PASSWORD'])

def clone_repo(clone_url):
    try:
        # Add user/pass to avoid issues for private repos; BEWARE -- this adds credentials to bash history
        clone_url = clone_url.replace("https://","https://{usr}:{pw}@"
            .format(usr=config['GITHUB_CREDENTIALS']['USERNAME'], pw=config['GITHUB_CREDENTIALS']['PASSWORD']))
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

def count_lines_of_code_to_sql_statements(project_name, dir, filename):
    """For directory dir, count lines of code, but generate output as SQL statements;
    on first call, create table. On subsequent calls, add 'sql-append' switch to append
    SQL statements to filename.

    @params
    project_name: allows cloc to differentiate input sources (ensure this is different from dir) and distinct bw calls
    dir: cloned repository name
    filename: file to write SQL statements to
    """
    try:
        args = ['cloc', '--sql', filename, '--sql-project', project_name, dir]
        if pathlib.Path(filename).exists(): 
            args.insert(args.index(dir), '--sql-append')
        subprocess.check_call(args)
    except subprocess.CalledProcessError as cpe:
        print(cpe.__cause__)

def main():
    # Initialize Github Client; get repository list
    _user, _pass = get_github_credentials()
    github_client = Github(_user, _pass)
    # db_name = config['SQLITE']['DBFILE']
    repo_list = github_client.get_user().get_repos()

    # Clear our SQL statements on a fresh run
    sql_statements_file = 'sql_statements'
    if pathlib.Path(sql_statements_file).exists():
        os.remove(sql_statements_file)

    # Count lines of code in each repo; however, output data as SQL statements
    for repo in repo_list:
        clone_repo(repo.clone_url)
        # count_lines_of_code_to_sqlite('p_{name}'.format(name=repo.name), repo.name, db_name)
        count_lines_of_code_to_sql_statements('p_{name}'.format(name=repo.name), repo.name, sql_statements_file)
        delete_repo(repo.name)

    # Initialize local database client connection; open cursor to perform db operations
    conn = psycopg2.connect("dbname={db} user={usr} password={pw}"
        .format(db=config['DB_CREDENTIALS']['DB_NAME'], usr=config['DB_CREDENTIALS']['USERNAME'],
        pw=config['DB_CREDENTIALS']['PASSWORD']))
    cur = conn.cursor()

    # In future, ensure database server is active and listening on port (currently 5432)
    
    # For every fresh run, delete tables. Might optimize later.
    cur.execute("drop table if exists t; drop table if exists metadata")

    # For each SQL statement, execute line
    with open(sql_statements_file) as ssf:
        filecontents = "".join(ssf.readlines())
        # Regex matches each single/multi-line statement ending in semi-colon
        for statement in re.findall(r"""([\S\s]+?;){1}""", filecontents):
            cur.execute(statement)

    # Ensure changes persist
    conn.commit()

    # Close communication channel with database
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
