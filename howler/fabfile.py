from fabric.api import local, settings, abort, run, cd, env
from fabric.contrib.console import confirm

env.hosts = ['10.0.10.180']  # Passphrase private key: hogehoge
env.project_root = '/var/www/howler'
code_dir = '/var/git/lukas-sandbox'

def test():
    with settings(warn_only=True):
        result = local('./manage.py test my_app', capture=True)
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")


def prepare_deploy():
    # test()
    # commit()
    push()


def deploy():
    #activate_pyenv()
    pull_copy()
    deploy_static()
    deploy_webserver()


def commit():
    local("git add -p && git commit")


def push():
    local("git push")


def activate_pyenv():
    run("pyenv shell howler")


def pull_copy():
    with cd(code_dir):
        run("git pull")
        run("cp -r /var/git/lukas-sandbox/howler/ /var/www/")


def deploy_static():
    with cd(env.project_root):
        run('./manage.py collectstatic -v0 --noinput')


def deploy_webserver():
    with cd(env.project_root):
        run("touch wsgi.py")