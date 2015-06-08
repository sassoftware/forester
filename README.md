Forester
========

Overview
--------
Manage multiple Git repositories from a single source file

Yes another for loop for git.

Build/Install
-------------
make
make install

Configuration
-------------

## Initialize configuration

forester init --branch bar --email foo@bar.com --name Joe Foo --wms --wmsbase http://foo.bar.com --wmspath silo/path --subdir ~/git --forest foo --common-aliases


## To add more Forests

forester init --branch master --wms --wmsbase http://foo.bar.com --wmspath silo/foobaz --subdir ~/git --forest foobaz

## To checkout forests

forester clone foobar foobaz foobuz
