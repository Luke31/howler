from fabric.api import local, settings, abort, run, cd, env, prefix
from fabric.contrib.files import sed
from fabric.contrib.console import confirm
import os

env.hosts = ['lukas@10.0.10.180']  # Passphrase private key: hogehoge
env.project_root = '/var/www/howler'
code_dir = '/var/git/lukas-sandbox'
python3_dir = '/home/lukas/.pyenv/versions/howler/bin'
wally_git = '-e git+ssh://lukas@gerrit.spicy.co-conv.jp:29418/lukas-sandbox.git#egg=wally&subdirectory=wally'


def deploy():
    """[Main] Deploy on server: Git Pull, Pip inst, Bower inst, Serve statics, Gen translations, Disable Debug,
    Migrate db, Restart app and apache"""
    pull_copy()
    pip_install()
    bower_install()
    deploy_static()
    compmsg()
    disable_debug_remote()  # TODO: Better: Use production configuration
    migrate_db()
    inform_webserver()
    restart_apache()


def pip_install():
    with cd(env.project_root):
        run('sudo pip3 install -r requirements.txt')  # apache uses this python3 version 3.4.2 (latest debian available)
        run(os.path.join(python3_dir, 'pip3') + ' install -r requirements.txt')  # installer python 3.5.2 (pyenv howler)
        # run('sudo pip3 install --upgrade --no-deps --force-reinstall {0}'.format(wally_git))
        # run(os.path.join(python3_dir, 'pip3') + ' install --upgrade --no-deps --force-reinstall {0}'.format(wally_git))


def pull_copy():
    """Git pull and copy to server place"""
    with cd(code_dir):
        run("git pull")
        run("cp -r /var/git/lukas-sandbox/howler/ /var/www/")


def bower_install():
    """Django bower install"""
    with cd(env.project_root):
        run(os.path.join(python3_dir, 'python') + ' ./manage.py bower install')


def deploy_static():
    """Django collect/deploy static files"""
    with cd(env.project_root):
        run(os.path.join(python3_dir, 'python') + ' ./manage.py collectstatic -v0 --noinput')


def compmsg():
    """Generate .mo file locally (gettext required)"""
    with cd(env.project_root):
        run('django-admin compilemessages')


def l_deploy_static():
    """[Local] Django collect/deploy static files"""
    with cd(env.project_root):
        local('python ./manage.py collectstatic -v0 --noinput')


def disable_debug_remote():
    """Disable debug mode in settings.py"""
    settings_path = os.path.join(env.project_root, 'howler', 'settings.py')
    sed(settings_path, "DEBUG = True", "DEBUG = False")


def l_genmsg():
    """[Local] Generate .po file locally (gettext required)"""
    # local('pyenv shell howler')
    local('django-admin makemessages -l ja --ignore=components')


def l_compmsg():
    """[Local] Generate .mo file locally (gettext required)"""
    # local('pyenv shell howler')
    local('django-admin compilemessages')


def migrate_db():
    """Migrate database"""
    with cd(env.project_root):
        run(os.path.join(python3_dir, 'python') + ' ./manage.py migrate')


def l_migrate_db():
    """[Local] Migrate database"""
    local("python manage.py migrate")


def inform_webserver():
    """trigger restart app (touch wsgi)"""
    with cd(env.project_root):
        run("touch wsgi.py")


def restart_apache():
    """trigger an apache service restart using sudo"""
    run("sudo /etc/init.d/apache2 restart")


def l_test():
    """[Local] Run Tests locally"""
    with settings(warn_only=True):
        result = local('./manage.py test my_app', capture=True)
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")
