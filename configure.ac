dnl Process this file with autoconf to produce a configure script.
AC_PREREQ([2.67])
AC_INIT([webengine-spv],[0.13.1])

AM_INIT_AUTOMAKE([foreign])
AM_PATH_PYTHON([2.5])

SJ_PROG_SJCONF
AC_PATH_PROG(MSGFMT, msgfmt)
AC_PATH_PROG(TXT2TAGS, txt2tags)

AC_SUBST([webenginedir], [\$\(datadir\)/webengine])
AC_SUBST([webenginesysconfdir], [\$\(sysconfdir\)/webengine])
AC_SUBST([webengineappdir], [\$\(webenginedir\)/app/webengine])
AC_SUBST([spvdir], [\$\(webengineappdir\)/spv])
AC_SUBST([mediasdir], [\$\(webenginedir\)/medias/spv])
AC_SUBST([mediascssdir], [\$\(mediasdir\)/css])
AC_SUBST([mediasimgdir], [\$\(mediasdir\)/img])
AC_SUBST([mediasjsdir], [\$\(mediasdir\)/js])
AC_SUBST([templatesdir], [\$\(webenginedir\)/templates/spv])
AC_SUBST([localesdir], [\$\(spvdir\)/locale])

AC_CONFIG_FILES([
	Makefile
	doc/Makefile
	templates/Makefile
	etc/Makefile
	medias/Makefile
	medias/css/Makefile
	medias/img/Makefile
	medias/js/Makefile
	locale/Makefile
	sjconf/Makefile
	sjconf/plugins/webengine-spv.py
	sjconf/templates/Makefile
	sjconf/templates/webengine-spv/Makefile
	sjconf/confs/Makefile
	sjconf/doc/Makefile
	data/Makefile
	])
AC_OUTPUT
