import configparser
from utils.file_utils import get_absolute_path
from github import Github

relative_path_from_utils_dir = '../../../.config/config.ini'

def get_github_credentials():
    config = configparser.ConfigParser()
    config.read(get_absolute_path(relative_path_from_utils_dir))
    return (config['GITHUB_CREDENTIALS']['USERNAME'], config['GITHUB_CREDENTIALS']['PASSWORD'])


def main():
    _user, _pass = get_github_credentials()
    github_client = Github(_user, _pass)
    for repo in github_client.get_user().get_repos():
        print(repo.name)

if __name__ == '__main__':
    main()
