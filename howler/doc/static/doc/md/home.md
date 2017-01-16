# Development documentation - Howler and Wally

This website is driven by a django-server running on Debian. Under [Production Environment](/howler/doc/env/) you can see the whole production system and under [Production Environment initial setup](/howler/doc/done/) you can see how it has been built. The main web django project `howler` (Git-repo: `lukas-sandbox/howler`) consists of following django applications:

* **wally_search** - Main search application for finding emails and IRC logs
* **settings** - Various settings for this search stored in a postgresql database - mainly managing synonyms
* **doc** - This documentation

For the search a self-developed python3-package `wally` (Git-repo: `lukas-sandbox/wally`) is used. It is used to search in text using elasticsearch and kuromoji. 

`wally` is also responsible for converting and sending raw emails to elasticsearch. To keep the indexed emails up-to-date an import script is used. For its usage see: [Email Import Script](/howler/doc/importscript/)

The IRC search uses the Elastic Stack. The search code is included in the `wally` package. For the indexation of the logs, logstash with Filebeat is used and the index is created using a python-script in the `wally` package. For further information see: [IRC Logstash](/howler/doc/irc/).   

If you would like to contribute to either to `howler` or `wally`, follow these steps:

### 1. Get repository
* Add your ssh public key to gerrit
* Replace lukas with your username
* Check ssh connection: `ssh -p 29418 lukas@gerrit.spicy.co-conv.jp`     
* Git clone: `git clone ssh://lukas@gerrit.spicy.co-conv.jp:29418/lukas-sandbox.git`
    
### 2. Get prereqs for development: Python and Virtualenvs

* Install python3: `sudo apt-get install python3-dev`

* Prepare virtualenv using pyenv (Has also been done on server (10.0.10.180):

    * Install pyenv to `~/.pyenv` according to tutorial: [Pyenv installation](https://github.com/yyuu/pyenv#installation)
    * Install pyenv-virtualenv to `~/.pyenv/plugins/pyenv-virtualenv` according to tutorial: [Pyenv-virtualenv - installing as pyenv plugin](https://github.com/yyuu/pyenv-virtualenv#installing-as-a-pyenv-plugin)
    * Set up virtualenv: `pyenv virtualenv 3.5.2 howler`
    * Set up automatic switch to virtualenv when in project folder:
    
            cd lukas-sandbox/howler
            pyenv local howler      # howler is a virtualenv of pyenv version 3.5.2
            cd ../howler            # Prompt should now preceed with a `(howler)`

    **Further sources:**
    [Cheatsheet - using pyenv with virtualenv and pip](https://fijiaaron.wordpress.com/2015/06/18/using-pyenv-with-virtualenv-and-pip-cheat-sheet/)
    and
    [Django Tutorial](http://docs.django-cms.org/en/release-3.4.x/introduction/install.html)

* Get IDE for Python3 and Django
    
    The project has initially been created with [PyCharm](https://www.jetbrains.com/pycharm/). But feel free to use any IDE.

### 3. Project Wally - Email parser, JSON converter, elasticsearch index client and IRC search and index creation:
* Python3 package `wally`, subfolder of git repository

**Develop for this package**
* Install requirements:

    * using the requirements file: `pip install -r requirements.txt`
 
    * or one-by-one:

            pip install --upgrade pip
            pip install cld2-cffi
            pip install elasticsearch
            pip install elasticsearch-dsl
* Edit in your IDE or...

**Use this package:** To use `wally` in another project e.g. `howler`, install it 
* from repo: `pip install -e 'git+ssh://lukas@gerrit.spicy.co-conv.jp:29418/lukas-sandbox.git#egg=wally&subdirectory=wally'`
* or using a relative path: `pip install -e ../wally/`

### 4. Project Howler - email and IRC-search with elasticsearch

* Django webapplication `howler`, subfolder of git repository

**Develop for this package**
* Install the required `wally` package using a relative path: `pip install -e ../wally/`. This will ensure that all changes to `wally` are instantly available in your `howler` project.
* Install python requirements using requirements file: `pip install -r requirements.txt`
* Edit in your IDE

**Use this package**
* Install python requirements using requirements file: `pip install -r requirements.txt`

### 5. Deployment of `howler` Django webapplication
To deploy `howler` fabric3 is used. This uses a deployment-script `fabfile.py` with multiple functions. The strength of fabric3 is 
that it may connect to the target deployment server and execute commands on them.

1. Install `Fabric3`: `pip install fabric3`
2. Go to project folder: `lukas-sandbox/howler`
3. See all deployment commands: `fab list`
4. **Main deployment** to target server is started using: `fab deploy` (When asked use password `hogehoge`)
5. Local commands:
    * `fab l_migrate_db` - Prepare db-migration script (Run this before deploying, add generated files to git and then deploy)
    * `fab l_makemsg` - Make .po files for translators 
    * `fab l_compmsg` - Compile .po files to binary .mo files for website:
    * `fab l_deploy_static` - Deploy static files locally:
6. Following useful remote-commands are available

    * `fab restart_es` - Restart elasticsearch on target server: 
    * `fab restart_apache` - Restart apache2 on target server

###Licensing

* Elasticsearch: [Apache-2.0](https://tldrlegal.com/license/apache-license-2.0-(apache-2.0))
