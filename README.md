# forester -- Archived Repository



**Notice: This repository is part of a Conary/rpath project at SAS that is no longer supported or maintained. Hence, the repository is being archived and will live in a read-only state moving forward. Issues, pull requests, and changes will no longer be accepted.**
 
Overview
--------
Manage multiple Git repositories from a single source file

Yes another for loop for git.

Build/Install
-------------
1. make
1. make install

Configuration
-------------

## Initialize configuration
```
forester init --branch bar --email foo@bar.com --name Joe Foo --wms --wmsbase http://foo.bar.com --wmspath silo/path --subdir ~/git --forest foo --common-aliases
```

## To add more Forests
```
forester init --branch master --wms --wmsbase http://foo.bar.com --wmspath silo/foobaz --subdir ~/git --forest foobaz
```

## To checkout forests
```
forester clone foobar foobaz foobuz
```
