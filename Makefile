classes.txt:
	python2 ./python/smartcard_enumerate_classes.py | sed -ne '3,$$p' > $@.tmp
	wc -l $@.tmp
	mv $@.tmp $@

xclasses:
	rm -f classes.txt
	$(MAKE) classes.txt

fuzzer:
	python2 ./python/smartcard_fuzzer.py

%-ins:
	python2 ./python/smartcard_discover_valid_inf.py $*
