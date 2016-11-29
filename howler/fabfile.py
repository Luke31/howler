from fabric.api import local, settings, abort, run, cd, env, prefix
from fabric.contrib.files import sed
from fabric.contrib.console import confirm
import os

env.hosts = ['lukas@10.0.10.180']  # Passphrase private key: hogehoge
env.project_root = '/var/www/howler'
code_dir = '/var/git/lukas-sandbox'
python3_dir = '/home/lukas/.pyenv/versions/howler/bin'


def test():
    with settings(warn_only=True):
        result = local('./manage.py test my_app', capture=True)
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")


def deploy():
    pull_copy()
    bower_install()
    deploy_static()
    disable_debug_remote()
    inform_webserver()


def pull_copy():
    with cd(code_dir):
        run("git pull")
        run("cp -r /var/git/lukas-sandbox/howler/ /var/www/")


def bower_install():
    with cd(env.project_root):
        run(os.path.join(python3_dir, 'python') + ' ./manage.py bower install')


def deploy_static():
    with cd(env.project_root):
        run(os.path.join(python3_dir, 'python') + ' ./manage.py collectstatic -v0 --noinput')


def disable_debug_remote():
    settings_path = os.path.join(env.project_root, 'howler', 'settings.py')
    sed(settings_path, "DEBUG = True", "DEBUG = False")


def inform_webserver():
    with cd(env.project_root):
        run("touch wsgi.py")

