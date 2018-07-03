%if 0%{?fedora} || 0%{?rhel} >= 8
%bcond_without python3
%else
%bcond_with python3
%endif

Name:           subunit
Version:        1.3.0
Release:        1%{?dist}
Summary:        C bindings for subunit

%global majver  %(cut -d. -f-2 <<< %{version})

License:        ASL 2.0 or BSD
URL:            https://launchpad.net/%{name}
Source0:        https://launchpad.net/%{name}/trunk/%{majver}/+download/%{name}-%{version}.tar.gz
# Fedora-specific patch: remove the bundled copy of python-iso8601.
Patch0:         %{name}-unbundle-iso8601.patch
# Merged upsteam: https://github.com/testing-cabal/subunit/pull/10
Patch1:         %{name}-decode-binary-to-unicode.patch

BuildRequires:  check-devel
BuildRequires:  cppunit-devel
BuildRequires:  gcc-c++
BuildRequires:  libtool
BuildRequires:  perl-generators
BuildRequires:  perl(ExtUtils::MakeMaker)
BuildRequires:  pkgconfig
BuildRequires:  python2-devel
BuildRequires:  python2-hypothesis
BuildRequires:  python2-docutils
BuildRequires:  python2-extras
BuildRequires:  python2-fixtures
BuildRequires:  python2-iso8601
BuildRequires:  python2-setuptools
BuildRequires:  python2-testscenarios
BuildRequires:  python2-testtools >= 1.8.0

%if %{with python3}
BuildRequires:  python3-devel
BuildRequires:  python3-docutils
BuildRequires:  python3-extras
BuildRequires:  python3-fixtures
BuildRequires:  python3-iso8601
BuildRequires:  python3-hypothesis
BuildRequires:  python3-setuptools
BuildRequires:  python3-testscenarios
BuildRequires:  python3-testtools >= 1.8.0
%endif

%description
Subunit C bindings.  See the python-subunit package for test processing
functionality.

%package devel
Summary:        Header files for developing C applications that use subunit
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Header files and libraries for developing C applications that use subunit.

%package cppunit
Summary:        Subunit integration into cppunit
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description cppunit
Subunit integration into cppunit.

%package cppunit-devel
Summary:        Header files for applications that use cppunit and subunit
Requires:       %{name}-cppunit%{?_isa} = %{version}-%{release}
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}
Requires:       cppunit-devel%{?_isa}

%description cppunit-devel
Header files and libraries for developing applications that use cppunit
and subunit.

%package perl
Summary:        Perl bindings for subunit
BuildArch:      noarch
Requires:       perl(:MODULE_COMPAT_%{perl_version})

%description perl
Subunit perl bindings.  See the python-subunit package for test
processing functionality.

%package shell
Summary:        Shell bindings for subunit
BuildArch:      noarch

%description shell
Subunit shell bindings.  See the python-subunit package for test
processing functionality.

%package -n python2-%{name}
Summary:        Streaming protocol for test results
BuildArch:      noarch
Requires:       python2-extras
Requires:       python2-iso8601
Requires:       python2-testtools >= 1.8.0

%{?python_provide:%python_provide python2-%{name}}

%description -n python2-%{name}
Subunit is a streaming protocol for test results.  The protocol is a
binary encoding that is easily generated and parsed.  By design all the
components of the protocol conceptually fit into the xUnit TestCase ->
TestResult interaction.

Subunit comes with command line filters to process a subunit stream and
language bindings for python, C, C++ and shell.  Bindings are easy to
write for other languages.

A number of useful things can be done easily with subunit:
- Test aggregation: Tests run separately can be combined and then
  reported/displayed together.  For instance, tests from different
  languages can be shown as a seamless whole.
- Test archiving: A test run may be recorded and replayed later.
- Test isolation: Tests that may crash or otherwise interact badly with
  each other can be run separately and then aggregated, rather than
  interfering with each other.
- Grid testing: subunit can act as the necessary serialization and
  deserialization to get test runs on distributed machines to be
  reported in real time.

%if %{with python3}
%package -n python3-%{name}
Summary:        Streaming protocol for test results
BuildArch:      noarch
Requires:       python3-extras
Requires:       python3-iso8601
Requires:       python3-testtools >= 1.8.0

%{?python_provide:%python_provide python3-%{name}}

%description -n python3-%{name}
Subunit is a streaming protocol for test results.  The protocol is a
binary encoding that is easily generated and parsed.  By design all the
components of the protocol conceptually fit into the xUnit TestCase ->
TestResult interaction.

Subunit comes with command line filters to process a subunit stream and
language bindings for python, C, C++ and shell.  Bindings are easy to
write for other languages.

A number of useful things can be done easily with subunit:
- Test aggregation: Tests run separately can be combined and then
  reported/displayed together.  For instance, tests from different
  languages can be shown as a seamless whole.
- Test archiving: A test run may be recorded and replayed later.
- Test isolation: Tests that may crash or otherwise interact badly with
  each other can be run separately and then aggregated, rather than
  interfering with each other.
- Grid testing: subunit can act as the necessary serialization and
  deserialization to get test runs on distributed machines to be
  reported in real time.
%endif

%package filters
Summary:        Command line filters for processing subunit streams
BuildArch:      noarch
Requires:       python2-%{name} = %{version}-%{release}
Requires:       pygtk2
Requires:       python2-junitxml

%description filters
Command line filters for processing subunit streams.

%package static
Summary:        Static C library for subunit
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}

%description static
Subunit C bindings in a static library, for building statically linked
test cases.


%prep
%setup -qc
%patch0
%patch1 -p1

fixtimestamp() {
  touch -r $1.orig $1
  rm $1.orig
}

# Help the dependency generator
for filt in filters/*; do
  sed 's,/usr/bin/env ,/usr/bin/,' $filt > ${filt}.new
  chmod 0755 ${filt}.new
  touch -r $filt ${filt}.new
  mv -f ${filt}.new $filt
done

# Fix underlinked library
sed "/^tests_LDADD/ilibcppunit_subunit_la_LIBADD = -lcppunit libsubunit.la\n" \
    -i Makefile.am

# Depend on python2, not just python
sed -i.orig 's,%{_bindir}/python,&2,' python/subunit/run.py
fixtimestamp python/subunit/run.py

# Do not use env
for fil in $(grep -Frl "%{_bindir}/env python"); do
  sed -i.orig 's,%{_bindir}/env python,%{_bindir}/python2,' $fil
  fixtimestamp $fil
done

# Replace bundled code with a symlink
ln -f -s %{python2_sitelib}/iso8601/iso8601.py python/subunit/iso8601.py

# Generate the configure script
autoreconf -fi

%if %{with python3}
# Prepare to build for python 3
cp -a ../%{name}-%{version} ../python3
mv ../python3 .
pushd python3
for fil in $(grep -Frl "%{_bindir}/python2"); do
  sed -i.orig 's,\(%{_bindir}/python\)2,\13,' $fil
  fixtimestamp $fil
done
ln -f -s %{python3_sitelib}/iso8601/iso8601.py python/subunit/iso8601.py
popd
%endif

%build
# Build for everything except python3
export INSTALLDIRS=perl
%configure --enable-shared --enable-static

# Get rid of undesirable hardcoded rpaths; workaround libtool reordering
# -Wl,--as-needed after all the libraries.
sed -e 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' \
    -e 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' \
    -e 's|CC=.g..|& -Wl,--as-needed|' \
    -i libtool

make %{?_smp_mflags}
%py2_build

# Build for python3
%if %{with python3}
pushd python3
export INSTALLDIRS=perl
export PYTHON=%{_bindir}/python3
%configure --enable-shared --enable-static

# Get rid of undesirable hardcoded rpaths; workaround libtool reordering
# -Wl,--as-needed after all the libraries.
sed -e 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' \
    -e 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' \
    -e 's|CC=.g..|& -Wl,--as-needed|' \
    -i libtool

make %{?_smp_mflags}
%py3_build
popd
%endif

%install
# Install for python 3 first so that the python 2 install overwrites files
%if %{with python3}
pushd python3
%py3_install
chmod 0755 %{buildroot}%{python3_sitelib}/%{name}/run.py

# Replace bundled code with a symlink again
ln -f -s %{python3_sitelib}/iso8601/iso8601.py \
   %{buildroot}%{python3_sitelib}/subunit/iso8601.py
for fil in iso8601.cpython-37.opt-1.pyc iso8601.cpython-37.pyc; do
  ln -f -s %{python3_sitelib}/iso8601/__pycache__/$fil \
     %{buildroot}%{python3_sitelib}/subunit/__pycache__/$fil
done

# Don't distribute the python tests
rm -fr %{buildroot}%{python3_sitelib}/subunit/tests

popd
%endif

# We set pkgpython_PYTHON for efficiency to disable automake python compilation
%make_install pkgpython_PYTHON='' INSTALL="%{_bindir}/install -p"

# Install the python interface
%py2_install

# Replace bundled code with a symlink again
for fil in iso8601.py iso8601.pyc iso8601.pyo; do
  ln -f -s %{python2_sitelib}/iso8601/$fil \
     %{buildroot}%{python2_sitelib}/subunit/$fil
done

# Install the shell interface
mkdir -p %{buildroot}%{_sysconfdir}/profile.d
cp -p shell/share/%{name}.sh %{buildroot}%{_sysconfdir}/profile.d

# Remove unwanted libtool files
rm -f %{buildroot}%{_libdir}/*.la

# Fix perl installation
mkdir -p %{buildroot}%{perl_vendorlib}
mv %{buildroot}%{perl_privlib}/Subunit* %{buildroot}%{perl_vendorlib}
rm -fr %{buildroot}%{perl_archlib}

# Fix permissions
chmod 0755 %{buildroot}%{python2_sitelib}/%{name}/run.py
chmod 0755 %{buildroot}%{_bindir}/subunit-diff

# Fix timestamps
touch -r c/include/%{name}/child.h %{buildroot}%{_includedir}/%{name}/child.h
touch -r c++/SubunitTestProgressListener.h \
      %{buildroot}%{_includedir}/%{name}/SubunitTestProgressListener.h
touch -r perl/subunit-diff %{buildroot}%{_bindir}/subunit-diff
for fil in filters/*; do
  touch -r $fil %{buildroot}%{_bindir}/$(basename $fil)
done

# Don't distribute the python tests
rm -fr %{buildroot}%{python2_sitelib}/subunit/tests

%check
# Run the tests for python2
export LD_LIBRARY_PATH=$PWD/.libs
export PYTHONPATH=$PWD/python/subunit:$PWD/python/subunit/tests
make check
# Make sure subunit.iso8601 is importable from buildroot
PYTHONPATH=%{buildroot}%{python2_sitelib} %{__python2} -c "import subunit.iso8601"

%if %{with python3}
# Run the tests for python3
pushd python3
export PYTHON=%{__python3}
make check
# Make sure subunit.iso8601 is importable from buildroot
PYTHONPATH=%{buildroot}%{python3_sitelib} %{__python3} -c "import subunit.iso8601"
popd
%endif

%ldconfig_scriptlets
%ldconfig_scriptlets cppunit

%files
%doc NEWS README.rst
%license Apache-2.0 BSD COPYING
%{_libdir}/lib%{name}.so.*

%files devel
%doc c/README
%dir %{_includedir}/%{name}/
%{_includedir}/%{name}/child.h
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/lib%{name}.pc

%files cppunit
%{_libdir}/libcppunit_%{name}.so.*

%files cppunit-devel
%doc c++/README
%{_includedir}/%{name}/SubunitTestProgressListener.h
%{_libdir}/libcppunit_%{name}.so
%{_libdir}/pkgconfig/libcppunit_%{name}.pc

%files perl
%license Apache-2.0 BSD COPYING
%{_bindir}/%{name}-diff
%{perl_vendorlib}/*

%files shell
%doc shell/README
%license Apache-2.0 BSD COPYING
%config(noreplace) %{_sysconfdir}/profile.d/%{name}.sh

%files -n python2-%{name}
%license Apache-2.0 BSD COPYING
%{python2_sitelib}/%{name}/
%{python2_sitelib}/python_%{name}-%{version}-*.egg-info

%if %{with python3}
%files -n python3-%{name}
%license Apache-2.0 BSD COPYING
%{python3_sitelib}/%{name}/
%{python3_sitelib}/python_%{name}-%{version}-*.egg-info
%endif

%files static
%{_libdir}/*.a

%files filters
%{_bindir}/*
%exclude %{_bindir}/%{name}-diff

%changelog
* Tue Jul  3 2018 Jerry James <loganjerry@gmail.com> - 1.3.0-1
- New upstream release
- Add -static subpackage (bz 1575054)

* Tue Jul 03 2018 Petr Pisar <ppisar@redhat.com> - 1.2.0-21
- Perl 5.28 rebuild

* Wed Jun 27 2018 Jitka Plesnikova <jplesnik@redhat.com> - 1.2.0-20
- Perl 5.28 rebuild

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 1.2.0-19
- Rebuilt for Python 3.7

* Mon Feb 12 2018 Iryna Shcherbina <ishcherb@redhat.com> - 1.2.0-18
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.0-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.0-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.0-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jun 26 2017 Jerry James <loganjerry@gmail.com> - 1.2.0-14
- Rebuild to fix broken perl dependencies

* Sun Jun 04 2017 Jitka Plesnikova <jplesnik@redhat.com> - 1.2.0-13
- Perl 5.26 rebuild

* Fri May  5 2017 Jerry James <loganjerry@gmail.com> - 1.2.0-12
- Rebuild for cppunit 1.14.0

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.0-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sun Jan 29 2017 Jerry James <loganjerry@gmail.com> - 1.2.0-10
- Add Requires on python-junitxml to -filter subpackage (bz 1417291)

* Tue Dec 20 2016 Miro Hrončok <mhroncok@redhat.com> - 1.2.0-9
- Rebuild for Python 3.6

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.0-8
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Fri Jun  3 2016 Jerry James <loganjerry@gmail.com> - 1.2.0-7
- Fix -python3 dependency on /usr/bin/python (bz 1342508)
- Comply with latest python packaging guidelines
- Drop workaround for bz 1251568, now fixed

* Sat May 14 2016 Jitka Plesnikova <jplesnik@redhat.com> - 1.2.0-6
- Perl 5.24 rebuild

* Mon Apr 18 2016 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> - 1.2.0-5
- Added missing check for %%with_py3 to make it buildable under RHEL/CentOS

* Sun Feb 14 2016 David Tardon <dtardon@redhat.com> - 1.2.0-4
- rebuild for cppunit 1.13.2

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Nov 10 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.0-2
- Rebuilt for https://fedoraproject.org/wiki/Changes/python3.5

* Fri Oct 23 2015 Jerry James <loganjerry@gmail.com> - 1.2.0-1
- New upstream release

* Wed Sep  2 2015 Haïkel Guémar <hguemar@fedoraproject.org> - 1.1.0-5
- Backport upstream patches (RHBZ#1259286)

* Fri Aug  7 2015 Jerry James <loganjerry@gmail.com> - 1.1.0-4
- Fix FTBFS due to older python-testtools (bz 1249714)

* Tue Jul 14 2015 Slavek Kabrda <bkabrda@redhat.com> - 1.1.0-3
- Symlink iso8601 file into subunit Python dirs to preserve compatibility while unbundling
Resolves: rhbz#1233581

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Jun 12 2015 Jerry James <loganjerry@gmail.com> - 1.1.0-1
- New upstream release
- Enable python3 tests

* Wed Jun 03 2015 Jitka Plesnikova <jplesnik@redhat.com> - 1.0.0-3
- Perl 5.22 rebuild

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 1.0.0-2
- Rebuilt for GCC 5 C++11 ABI change

* Tue Dec  9 2014 Jerry James <loganjerry@gmail.com> - 1.0.0-1
- New upstream release (bz 1171483 and 1172204)
- Add python3 subpackage (bz 1172195)

* Wed Nov 19 2014 Pádraig Brady <pbrady@redhat.com> - 0.0.21-2
- Make python-subunit egginfo available for pip etc.

* Fri Sep 19 2014 Jerry James <loganjerry@gmail.com> - 0.0.21-1
- New upstream release
- Fix license handling

* Wed Aug 27 2014 Jitka Plesnikova <jplesnik@redhat.com> - 0.0.18-5
- Perl 5.20 rebuild

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.18-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.18-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Apr 24 2014 Jerry James <loganjerry@gmail.com> - 0.0.18-2
- Add license text to all independent packages
- Add perl module Requires to the -perl subpackage
- Fix timestamps after install

* Fri Feb 14 2014 Jerry James <loganjerry@gmail.com> - 0.0.18-1
- Initial RPM
