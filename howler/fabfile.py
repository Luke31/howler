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


def prepare_deploy():
    # test()
    # commit()
    push()


def deploy():
    pull_copy()
    deploy_static()
    disable_debug()
    inform_webserver()

def commit():
    local("git add -p && git commit")


def push():
    local("git push")


def pull_copy():
    with cd(code_dir):
        run("git pull")
        run("cp -r /var/git/lukas-sandbox/howler/ /var/www/")


def deploy_static():
    with cd(env.project_root):
        run(os.path.join(python3_dir,'python') + ' ./manage.py collectstatic -v0 --noinput')

def disable_debug():
    with cd(os.path.join(env.project_root,'howler')):
        run()


def inform_webserver():
    with cd(env.project_root):
        run("touch wsgi.py")


def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/superlists/settings.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(settings_path, 'DOMAIN = "localhost"', 'DOMAIN = "%s"' % (site_name,))