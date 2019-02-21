# Email Import Script

To keep the elasticsearch index up-to-date a python email import script is used.
This script is located in the Git-repo at `lukas-sandbox/wally/index-cmd.py` and provides a command-line interface to update elasticsearch index with new emails.

##How to install this package for script-usage
1. Install pip3: 

        sudo apt-get install python3-pip

2. Download this package with its script: 

        git clone ssh://git@github.com:Luke31/howler.git

    or just copy it to any directory

3. Go to installed directory -> project wally
        
        cd lukas-sandbox/wally

3. Install the required python modules (You may also create a virtualenv for this):
        
        pip3 install -r requirements.txt

##How to use this script to get help
    python3 index-cmd.py -h
    python3 index-cmd.py update -h


## Basic usage (also visible when calling the help)
* Update new mails from folder `data_in` to es-server `10.0.10.180` (e.g. for **Cron-usage**):

        python3 index-cmd.py update data_in 10.0.10.180
        
* Update force all mails from folder `data_in` to es-server `10.0.10.180` with (deletes existing indices):

        python3 index-cmd.py update data_in 10.0.10.180 --force
        
* Single mail file `data_in/99992` to es-server `10.0.10.180`:

        python3 index-cmd.py update data_in/99992 10.0.10.180

## Test execution with real files (Cron-example)

    cd /home/lukas/git-local/lukas-sandbox/wally
    git pull        # update wally-package to get newest version (use password hogehoge if asked)
    python3 index-cmd.py update /home/saita/archive/info 10.0.10.180
    
## Crontab daily

For a daily execution a CRON-job has been created. The job is run as user `lukas` and runs daily at 3am.

    0 3 * * * python3 /home/lukas/git-local/lukas-sandbox/wally/index-cmd.py update /home/saita/archive/info 10.0.10.180 >> /var/log/wally/email-importscript.log 2>&1

Log-file: `/var/log/wally/email-importscript.log`

To see crontab for user `lukas`, run: `sudo crontab -u lukas -l`
