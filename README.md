# Rest-api for azure

Starting with the python-rest-api hello world, upgrading step-by-step

### 04.March 2018

The "full-blown" API does not work. going back to the "hello, world" version

- Commit: "back to hello-world in main.py" --> not importing anything from resources

Doesn't work on Azure (works on localhost). Removing all imports (from resources,
API, etc.).

- Commit: "removed imports from resources, ..."
THIS WORKS!

- Commit: "added import from quote"
uncommented: from resources.quote import Quote_test (not used)
DOES NOT work

- Commit: "commented out imports from quote"
no imports from models within resources.quote
DOES NOT work

- Quick test:
New Python 3.4 environment, pip install -r requirements.txt
Works also

- New approach: create a CLI account and push from the console



- added git remote azure. git remote and url:
https://oldenhofe@prometheon-rest-api-cli-2.scm.azurewebsites.net/prometheon-rest-api-cli-2.git
prometheon-rest-api-cli-2.azurewebsites.net

- removed the import from resources to check whether the git push to azure works
Deployment with CLI works! (postman and chrome: "hello, world!")
