Boautomate
==========

Generic automation tool. A framework for writing automation scripts in Python.
It is not a fully featured CI like Jenkins, but a very lightweight CI-like server and framework.

**Features:**

- Pipelines (like in Jenkins CI, but in Python)
- Configuration and pipeline scripts stored in code (git/s3/local fs/more)
- Incoming payload is parsed into FACTS (ex. github push into repository context fact)
- Huge flexibility
- Supports multiple executors ex. run pipelines in local or remote docker, run pipelines as local scripts, run pipelines as remote script via ssh
- Multiple nodes. The node does not need any software extra installed except SSH+Python or Docker


**Requirements:**

- Python 3.7+ (with all libraries listed in `requirements.txt`)
- Linux
- Docker (optionally for docker support and execution in docker containers)
-

**Why?**

Boautomate was created to be a ultra lightweight alternative to Jenkins, as not everybody can afford to host
a big dinosaur that eats at least 4 GiB of RAM, just to write ex. a few scripts that will be taking GIT or Docker Registry webhooks,
processing and calling some external services, updating a file in a git repository, or building a documentation.

**Example scenarios for Boautomate**

a) boautomate/push-tags.py

Listen for a new tag built on Docker Registry ex. Quay.io. When a version is tagged, ex. 6.1.4, then push 6.1.4 to 6.1 and 6 and "latest-stable".

b) boautomate/update-version-docs.py

When a new application version comes, then open a "VERSIONS.rst" on "master" git branch, append new version to the list, commit and push.

**Running the test/preview version of Boautomate**

.. code:: bash

    # in first console
    make run_test_server

    # in second console
    make run_test_pipeline
