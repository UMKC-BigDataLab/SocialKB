Test the trends collection code by execeuting the script ./trender.sh

To make trends collection run automaticlly, create a cron job by executing the command "crontab -e" and adding the follwoing line:

00 * * * * /<path-to>/trender.sh

This will run the script every hour. Refer to http://www.cyberciti.biz/faq/how-do-i-add-jobs-to-cron-under-linux-or-unix-oses/
for more info and how to change the frequency.

