# Keep directory structure in VCS to allow use of django tools while developing

nobase_locales_DATA = \
	en/LC_MESSAGES/django.mo \
	fr/LC_MESSAGES/django.mo

SUFFIXES: .po

.po.mo:
	-@localebuildir=`echo $@ | sed 's:\(.*/\).*:\1:'` \
	  && test ! -d "$$localebuildir" && $(MKDIR_P) $$localebuildir
	$(MSGFMT) --check-format -o $@ $<

EXTRA_DIST = fr en
CLEANFILES = $(nobase_locales_DATA)
