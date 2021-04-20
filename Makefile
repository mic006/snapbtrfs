.NOTPARALLEL:

all:
qt: q t
q: quality
t: test

# to be launched as root
INSTALL_DEST = /utils
install:
	cp snapbtrfs.py $(INSTALL_DEST)
	sed -i "s/VERSION:.*/VERSION: $(shell git describe --tags --always --dirty)/" $(INSTALL_DEST)/snapbtrfs.py
	sed -i "s/DEBUG = True/DEBUG = False/" $(INSTALL_DEST)/snapbtrfs.py

quality:
	-pylint --rcfile /etc/pylint.rc *.py

test:
	python -m unittest -v

.PHONY: all install qt q t quality test