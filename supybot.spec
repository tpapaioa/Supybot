%global origname supybot
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           supybot
Version:        0.83.4.2
Release:        1%{?dist}
Summary:        Cross-platform IRC bot written in Python

Group:          Applications/Internet
# The entire source code is BSD except for
# Supybot-0.83.4/plugins/Math/local/convertcore.py which is GPLv2
License:        BSD and GPLv2
URL:            http://supybot.com
Source:         %{name}-%{version}.tar.gz
BuildArch:      noarch
BuildRequires:  python-setuptools

Requires:       python-twisted-core
Requires:       python-twisted-names
Requires:       python-dateutil
Requires:       python-feedparser
Requires:       python-dictclient
Requires:       python-simplejson
Provides:       Supybot = %{version}-%{release}
Conflicts:	supybot-gribble

%description
Supybot is a robust, user-friendly, and programmer-friendly Python IRC bot.
It aims to be an adequate replacement for most existing IRC bots.  It
includes a very flexible and powerful ACL system for controlling access
to commands, as well as more than 50 builtin plugins providing around
400 actual commands.

%prep
%setup -q -n %{origname}-%{version}

# %patch0 -p1
# %patch1 -p1


%build
CFLAGS="%{optflags}" %{__python} -c 'import setuptools; execfile("setup.py")' build


%install
%{__rm} -rf %{buildroot}
%{__python} -c 'import setuptools; execfile("setup.py")' install \
    --skip-build --root %{buildroot}

%{__install} -d -m 755 %{buildroot}%{_mandir}/man1/
%{__install} -m 644 docs/man/supybot.1 %{buildroot}%{_mandir}/man1/
%{__install} -m 644 docs/man/supybot-adduser.1 %{buildroot}%{_mandir}/man1/
%{__install} -m 644 docs/man/supybot-botchk.1 %{buildroot}%{_mandir}/man1/
%{__install} -m 644 docs/man/supybot-plugin-create.1 %{buildroot}%{_mandir}/man1/
%{__install} -m 644 docs/man/supybot-plugin-doc.1 %{buildroot}%{_mandir}/man1/
%{__install} -m 644 docs/man/supybot-test.1 %{buildroot}%{_mandir}/man1/
%{__install} -m 644 docs/man/supybot-wizard.1 %{buildroot}%{_mandir}/man1/

%{__install} -d -m 755 _docs_staging/
%{__install} -m 644 docs/ADVANCED_PLUGIN_CONFIG.rst _docs_staging/ADVANCED_PLUGIN_CONFIG
%{__install} -m 644 docs/ADVANCED_PLUGIN_TESTING.rst _docs_staging/ADVANCED_PLUGIN_TESTING
%{__install} -m 644 docs/CAPABILITIES.rst _docs_staging/CAPABILITIES
%{__install} -m 644 docs/CONFIGURATION.rst _docs_staging/CONFIGURATION
%{__install} -m 644 docs/FAQ.rst _docs_staging/FAQ
%{__install} -m 644 docs/GETTING_STARTED.rst _docs_staging/GETTING_STARTED
%{__install} -m 644 docs/PLUGIN_TUTORIAL.rst _docs_staging/PLUGIN_TUTORIAL
%{__install} -m 644 docs/STYLE.rst _docs_staging/STYLE
%{__install} -m 644 docs/USING_UTILS.rst _docs_staging/USING_UTILS
%{__install} -m 644 docs/USING_WRAP.rst _docs_staging/USING_WRAP

# These are provided in python-feedparser, python-dateutil,
# python-dictclient, and python-simplejson
%{__rm} -rf %{buildroot}%{python_sitelib}/supybot/plugins/RSS/local
%{__rm} -rf %{buildroot}%{python_sitelib}/supybot/plugins/Time/local
%{__rm} -rf %{buildroot}%{python_sitelib}/supybot/plugins/Dict/local
%{__rm} -rf %{buildroot}%{python_sitelib}/supybot/plugins/Google/local


%clean
%{__rm} -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc ACKS ChangeLog LICENSE README RELNOTES
%doc _docs_staging/{ADVANCED_PLUGIN_CONFIG,ADVANCED_PLUGIN_TESTING,CAPABILITIES}
%doc _docs_staging/{CONFIGURATION,FAQ,GETTING_STARTED,PLUGIN_TUTORIAL,STYLE}
%doc _docs_staging/{USING_UTILS,USING_WRAP}
%{python_sitelib}/*egg-info
%{python_sitelib}/supybot
%{_bindir}/supybot
%{_bindir}/supybot-adduser
%{_bindir}/supybot-botchk
%{_bindir}/supybot-plugin-create
%{_bindir}/supybot-plugin-doc
%{_bindir}/supybot-test
%{_bindir}/supybot-wizard
%{_mandir}/man1/supybot.1*
%{_mandir}/man1/supybot-adduser.1*
%{_mandir}/man1/supybot-botchk.1*
%{_mandir}/man1/supybot-plugin-create.1*
%{_mandir}/man1/supybot-plugin-doc.1*
%{_mandir}/man1/supybot-test.1*
%{_mandir}/man1/supybot-wizard.1*


%changelog
* Tue Jan 05 2016 Anastasios Y. Papaioannou <tpapaioa@redhat.com> - 0.83.4.2-1
- SQL fixes
* Mon Dec 28 2015 Anastasios Y. Papaioannou <tpapaioa@redhat.com> - 0.83.4.1-1
- Initial build of fork
