init:
	sudo apt install gir1.2-snapd-1 zenity python3-nose

test:
	nosetests tests -v
