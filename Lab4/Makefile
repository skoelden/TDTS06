# -*- Mode: Makefile -*-
#
# Makefile - Java version
#
# use: make
# or:  make test
#

JAVA = /usr/bin/java
JAVAC = /usr/bin/javac

all: RouterSimulator.class RouterPacket.class RouterNode.class GuiTextArea.class

RouterSimulator.class: RouterSimulator.java
	-@$(JAVAC) RouterSimulator.java

RouterPacket.class: RouterPacket.java
	-@$(JAVAC) RouterPacket.java

RouterNode.class: RouterNode.java
	-@$(JAVAC) RouterNode.java

GuiTextArea.class: GuiTextArea.java
	-@$(JAVAC) GuiTextArea.java

clean:
	-@touch ./abc~ core
	-@rm -f *~ core

clobber: clean
	-@touch ./abc.class
	-@rm -f *.class

test: all
	$(JAVA) -DTrace=3 RouterSimulator

install3:
	-@echo
	-@echo "  Warning: this command will overwrite file ./RouterSimulator.java"
	-@echo
	-@echo "Continue with ^D, exit with ^C"
	-@cat > /dev/null
	-@make clobber
	-@cp test/RouterSimulator3.java RouterSimulator.java

install4:
	-@echo
	-@echo "  Warning: this command will overwrite file ./RouterSimulator.java"
	-@echo
	-@echo "Continue with ^D, exit with ^C"
	-@cat > /dev/null
	-@make clobber
	-@cp test/RouterSimulator4.java RouterSimulator.java

install5:
	-@echo
	-@echo "  Warning: this command will overwrite file ./RouterSimulator.java"
	-@echo
	-@echo "Continue with ^D, exit with ^C"
	-@cat > /dev/null
	-@make clobber
	-@cp test/RouterSimulator5.java RouterSimulator.java
