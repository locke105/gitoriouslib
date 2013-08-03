============
gitoriouslib
============

gitoriouslib is a basic python API that interacts
with Gitorious, a Git repository hosting software.

It has basic functionality for creating and deleting
repositories when pointed at a Gitorious service and given
credentials for interacting with the service.

usage
=====

After cloning the source repository, install the CLI scripts and
library files by running the setup.py installer from the project directory::

 python setup.py install

Copy etc/gitoriouslib.conf.sample to ~/.gitoriouslib.conf and edit
accordingly with your Gitorious and credential information.

Now you should be able to create/delete projects in Gitorious with
the 'glcreate' and 'gldelete' scripts::

 # create a repository named "mynewrepo" in the "myproject" project
 glcreate myproject mynewrepo
 # delete the repository we just made
 gldelete myproject mynewrepo

