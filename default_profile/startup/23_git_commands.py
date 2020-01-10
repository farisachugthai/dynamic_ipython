import subprocess

try:
    import git
except:
    git = None
else:
    from git import Git


def generate_git_aliases():
    pass


def git_cur_branch():
    return subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
