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

- Commit: "commented out imports from quote"
no imports from models
