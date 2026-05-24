# 2605_DS5111_ced9mq
GitHub respository for DS 5111 work (Summer 2026)

## New VM Set up

Pre-Set up Requirements: 
* User has launched an established AWS EC2 instance
* User has created and set up an SSH key to enable login to GitHub with credentials

VM Set up Steps:  
1. Clone the GitHub repository to the VM with `git clone git@github.com:cedozier/2605_DS5111_ced9mq.git`  
2. cd into the GitHub repository `2605_DS5111_ced9mq` from the root  
3. cd into `scripts`  
4. Run `bash init.sh` to make sure the VM is update-to-date and has the required programs/tools installed (make/python/tree)
5. Run `bash init_git_creds.sh` to configure GitHub credentials (when run it will echo email/username)  
6. cd back to the root of the repository  
7. Run `make update` to execute the `makefile` that creates the virtual environment for Python and loads the required packages (calls the `requirements.txt` file present in the repo)  
8. Test success by running `. env/bin/activate` to confirm the new virtual environment can be activated (this activates it) and `pip list` to ensure required packages are present  


