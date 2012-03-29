dnl Process this file with autoconf to produce a configure script.
AC_PREREQ([2.67])
AC_INIT([webengine-spv],[0.14.0])

AM_INIT_AUTOMAKE([foreign])
AM_PATH_PYTHON([2.5])

SJ_PROG_SJCONF
AC_PATH_PROG(MSGFMT, msgfmt)
AC_PATH_PROG(TXT2TAGS, txt2tags)

AC_SUBST([webenginedir], [\$\(datadir\)/webengine])
AC_SUBST([webenginesysconfdir], [\$\(sysconfdir\)/webengine])
AC_SUBST([webengineappdir], [\$\(webenginedir\)/app/webengine])
AC_SUBST([spvdir], [\$\(webengineappdir\)/spv])

AC_CONFIG_FILES([
	Makefile
	doc/Makefile
	etc/Makefile
	sjconf/Makefile
	sjconf/plugins/webengine-spv.py
	sjconf/templates/Makefile
	sjconf/templates/webengine-spv/Makefile
	sjconf/confs/Makefile
	sjconf/doc/Makefile
	data/Makefile
	])
AC_OUTPUT
