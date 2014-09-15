
SUBCOMMANDS=clone config init merge pull

.PHONY: all clean rm_phony_commands phony_commands troff 

all: troff rm_phony_commands

clean: rm_phony_commands
	rm *.1

rm_phony_commands:
	rm ./forester
	for subcommand in $(SUBCOMMANDS); do \
	    rm ./forester-$$subcommand; \
	done

phony_commands:
	printf "%s\n\n%s\n" "#/bin/sh" 'PYTHONPATH=../.. python ../../commands/forester "$$@"' \
	    > ./forester
	chmod 700 ./forester
	for subcommand in $(SUBCOMMANDS); do \
	    printf "%s\n\n%s\n" "#/bin/sh" \
	    	"PYTHONPATH=../.. python ../../commands/forester $$subcommand \"\$$@\"" \
		> ./forester-$$subcommand; \
	    chmod 700 ./forester-$$subcommand; \
	done

troff: phony_commands
	help2man --no-info --include=forester.help2man --name="manage a forest of git trees" \
	    ./forester > forester.1
	for subcommand in $(SUBCOMMANDS); do \
	     help2man --no-info --include=forester.help2man \
	     	--opt-include=forester-$$subcommand.help2man ./forester-$$subcommand \
		> forester-$$subcommand.1; \
	done
