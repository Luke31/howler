# Howler and Wally - Development documentation

This website is driven by a django-server running on a Debian. For the search following python-package is used:

* wally (Search in text, using elasticsearch and kuromoji)
    
    * Elasticsearch DSL or (low-level elasticsearch-py)

## Get repository
* Add your ssh public key to gerrit
* Replace lukas with your username
* Check ssh connection: `ssh -p 29418 lukas@gerrit.spicy.co-conv.jp`     
* Git clone: `git clone ssh://lukas@gerrit.spicy.co-conv.jp:29418/lukas-sandbox.git`
    
## Prereqs for development: Python and Virtualenvs
[Cheatsheet - using pyenv with virtualenv and pip](https://fijiaaron.wordpress.com/2015/06/18/using-pyenv-with-virtualenv-and-pip-cheat-sheet/)

[Django Tutorial]()http://docs.django-cms.org/en/release-3.4.x/introduction/install.html)

**DONE-STEPS on Server (10.0.10.180)**

* pyenv  `~/.pyenv` https://github.com/yyuu/pyenv
* python (3.5.2)
* pyenv-virtualenv `~/.pyenv/plugins/pyenv-virtualenv` https://github.com/yyuu/pyenv-virtualenv
	(Auto-init)
* kibana

http://blog.mathieu-leplatre.info/deploy-django-projects-using-git-push.html#id3
	
* pyenv virtualenv 3.5.2 wally_search
pyenv virtualenv wally_search (SAME if only one python or 3.5.2 activated)

**pyenv activate wally_search - not needed - https://github.com/yyuu/pyenv-virtualenv#activate-virtualenv**

**If eval "$(pyenv virtualenv-init -)" is configured in your shell, pyenv-virtualenv will automatically activate/deactivate virtualenvs on entering/leaving directories which contain a .python-version file that lists a valid virtual environment. .python-version files denote local Python versions and can be created and deleted with the pyenv local command.**

Instead: 

    mkdir wally_search
    cd wally_search
    pyenv local wally_search     # wally_search is a virtualenv of pyenv version 3.5.2
    cd ../wally_search  # Prompt should now preceed with a `(wally_search)`


## Wally - Email parser and JSON converter (Python3 package)
* Install requirements single:

        pip install --upgrade pip
        pip install cld2-cffi
        pip install elasticsearch
        pip install elasticsearch-dsl
    
* Install python requirements using requirements file: `pip install -r requirements.txt`

* Install from repo: `pip install -e 'git+ssh://lukas@gerrit.spicy.co-conv.jp:29418/lukas-sandbox.git#egg=wally&subdirectory=wally'`

* Install Relative: `pip install -e ../wally/`

## Howler - email-search with elasticsearch (Django webapplication)

