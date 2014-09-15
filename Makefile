#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


all: all-subdirs default-all

all-subdirs:
	for d in $(SUBDIRS); do make -C $$d DIR=$$d || exit 1; done

export TOPDIR = $(shell pwd)
export TIMESTAMP = $(shell python -c "import time; print time.time(); exit;")
export CFGDEVEL=rpathrc

SUBDIRS=forester commands
MANPAGES=$(notdir $(filter %.1,$(wildcard docs/manpages/*.1)))

extra_files = \
	Make.rules 		\
	Makefile		\
	Make.defs		\
	NEWS			\
	README			\
	LICENSE			\
	TODO			\
	WIKI


.PHONY: clean dist install subdirs html

subdirs: default-subdirs

install: install-subdirs

clean: clean-subdirs default-clean

man:
	mkdir -p $(DESTDIR)$(mandir)/man1 
	for M in $(MANPAGES); do \
		install -m 0644 docs/manpages/$$M $(DESTDIR)$(mandir)/man1/; \
		gzip $(DESTDIR)$(mandir)/man1/$$M; \
	done

archive:
		git archive --format=tar --prefix=forester-$(VERSION)/ HEAD | gzip -9c > forester-$(VERSION).tar.gz

tag:
	git tag forester-$(VERSION)

clean: clean-subdirs default-clean 

include Make.rules
include Make.defs
 
# vim: set sts=4 sw=4 noexpandtab :
