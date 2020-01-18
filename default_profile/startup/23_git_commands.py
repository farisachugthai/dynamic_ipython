import subprocess

try:
    from git import Git
except:
    Git = None
else:
    from git import Repo
    # repo = Repo()


def generate_git_aliases():
    pass


def git_cur_branch():
    return subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
