KCONFIG_SRCDIR := kconfig
LDIALOG_SRCDIR := $(KCONFIG_SRCDIR)/lxdialog
INCLUDE_SRCDIR := include

CC := gcc
CXX := g++
FLEX := flex
BISON := bison
MOC := moc
PKG_CONFIG := pkg-config

BINDIR := bin

OBJDIR := obj

CPPFLAGS := -I$(KCONFIG_SRCDIR) -I. -I$(INCLUDE_SRCDIR) -I$(OBJDIR) $(shell $(PKG_CONFIG) --cflags Qt5Core Qt5Gui Qt5Widgets) $(shell $(PKG_CONFIG) --cflags gtk+-3.0)
CFLAGS := -O2
CXXFLAGS := -O2 -std=c++11 -fPIC
LDFLAGS := 

COMMON_SRCS := confdata.c expr.c menu.c preprocess.c symbol.c util.c

GENERATED_SRCS := lexer.lex.c parser.tab.c parser.tab.h

# Common object files
COMMON_OBJS := $(addprefix $(OBJDIR)/, $(patsubst %.c,%.o,$(COMMON_SRCS)))
COMMON_OBJS += $(addprefix $(OBJDIR)/, lexer.lex.o parser.tab.o)

# conf sources and objects
CONF_SRCS := conf.c
CONF_OBJS := $(addprefix $(OBJDIR)/, $(patsubst %.c,%.o,$(CONF_SRCS)))

# nconf sources and objects
NCONF_SRCS := nconf.c nconf.gui.c mnconf-common.c
NCONF_OBJS := $(addprefix $(OBJDIR)/, $(patsubst %.c,%.o,$(NCONF_SRCS)))

# mconf sources and objects
LDIALOG_SRCS := $(wildcard $(LDIALOG_SRCDIR)/*.c)
LDIALOG_OBJS := $(patsubst $(LDIALOG_SRCDIR)/%.c,$(OBJDIR)/lxdialog_%.o,$(LDIALOG_SRCS))
MCONF_SRCS := mconf.c mnconf-common.c
MCONF_OBJS := $(addprefix $(OBJDIR)/, $(patsubst %.c,%.o,$(MCONF_SRCS)))

# qconf sources and objects
QCONF_SRCS := qconf.cc images.c
QCONF_OBJS := $(addprefix $(OBJDIR)/, $(patsubst %.cc,%.o,$(filter %.cc,$(QCONF_SRCS))))
QCONF_OBJS += $(addprefix $(OBJDIR)/, $(patsubst %.c,%.o,$(filter %.c,$(QCONF_SRCS))))
QCONF_OBJS += $(OBJDIR)/qconf-moc.o

# gconf sources and objects
GCONF_SRCS := gconf.c images.c
GCONF_OBJS := $(addprefix $(OBJDIR)/, $(patsubst %.c,%.o,$(filter %.c,$(GCONF_SRCS))))

# Targets
all: $(BINDIR)/conf $(BINDIR)/nconf $(BINDIR)/mconf $(BINDIR)/qconf $(BINDIR)/gconf

$(BINDIR)/conf: $(COMMON_OBJS) $(CONF_OBJS)
	$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ $(COMMON_OBJS) $(CONF_OBJS) $(LDFLAGS)

$(BINDIR)/nconf: $(COMMON_OBJS) $(NCONF_OBJS)
	$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ $(COMMON_OBJS) $(NCONF_OBJS) $(LDFLAGS) -lncurses -lmenu -lpanel

$(BINDIR)/mconf: $(COMMON_OBJS) $(MCONF_OBJS) $(LDIALOG_OBJS)
	$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ $(COMMON_OBJS) $(MCONF_OBJS) $(LDIALOG_OBJS) $(LDFLAGS) -lcurses

$(BINDIR)/qconf: $(COMMON_OBJS) $(QCONF_OBJS)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -o $@ $(COMMON_OBJS) $(QCONF_OBJS) $(LDFLAGS) $(shell $(PKG_CONFIG) --libs Qt5Core Qt5Gui Qt5Widgets)

$(BINDIR)/gconf: $(COMMON_OBJS) $(GCONF_OBJS)
	$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ $(COMMON_OBJS) $(GCONF_OBJS) $(LDFLAGS) $(shell $(PKG_CONFIG) --libs gtk+-3.0)

$(shell mkdir -p $(OBJDIR))
$(shell mkdir -p $(BINDIR))

$(OBJDIR)/%.o: $(KCONFIG_SRCDIR)/%.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

# Compilation rules for nconf sources
$(OBJDIR)/nconf.o: $(KCONFIG_SRCDIR)/nconf.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

$(OBJDIR)/nconf.gui.o: $(KCONFIG_SRCDIR)/nconf.gui.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

$(OBJDIR)/mnconf-common.o: $(KCONFIG_SRCDIR)/mnconf-common.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

# Compilation rules for mconf sources
$(OBJDIR)/mconf.o: $(KCONFIG_SRCDIR)/mconf.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

# Compilation rules for lxdialog sources
$(OBJDIR)/lxdialog_%.o: $(LDIALOG_SRCDIR)/%.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

# Compilation rules for qconf sources
$(OBJDIR)/qconf.o: $(KCONFIG_SRCDIR)/qconf.cc
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c -o $@ $<

$(OBJDIR)/images.o: $(KCONFIG_SRCDIR)/images.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

$(OBJDIR)/qconf-moc.o: $(OBJDIR)/qconf-moc.cc
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c -o $@ $<

$(OBJDIR)/qconf-moc.cc: $(KCONFIG_SRCDIR)/qconf.h
	$(MOC) $(KCONFIG_SRCDIR)/qconf.h -o $@

# Lexer and parser rules
$(OBJDIR)/lexer.lex.o: $(OBJDIR)/lexer.lex.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $(OBJDIR)/lexer.lex.c

$(OBJDIR)/lexer.lex.c: $(KCONFIG_SRCDIR)/lexer.l $(OBJDIR)/parser.tab.h
	$(FLEX) -o $@ $<

$(OBJDIR)/parser.tab.o: $(OBJDIR)/parser.tab.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -DYYDEBUG -c -o $@ $(OBJDIR)/parser.tab.c

$(OBJDIR)/parser.tab.c $(OBJDIR)/parser.tab.h: $(KCONFIG_SRCDIR)/parser.y
	$(BISON) -d --verbose -o $(OBJDIR)/parser.tab.c $<

.PHONY: all clean

clean:
	rm -rf $(BINDIR) $(OBJDIR)
