dist_man7_MANS = webengine-spv-services.man
dist_man5_MANS = webengine-spv.conf.man

CLEANFILES = $(dist_man7_MANS) $(dist_man5_MANS)
EXTRA_DIST = $(wildcard $(srcdir)/*.t2t)

SUFFIXES = .t2t

.t2t.man:
	$(TXT2TAGS) -o $@ $<
