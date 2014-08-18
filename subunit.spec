# There is no python3 subpackage due to lack of a python3 variant of
# testscenarios (see https://bugs.launchpad.net/testscenarios/+bug/941963).
# Once that has been resolved, a python3 subpackage will be produced.

Name:           subunit
Version:        0.0.18
Release:        4%{?dist}
Summary:        C bindings for subunit

License:        ASL 2.0 or BSD
URL:            https://launchpad.net/%{name}
Source0:        https://launchpad.net/%{name}/trunk/%{version}/+download/%{name}-%{version}.tar.gz
# Fedora-specific patch: remove the bundled copy of python-iso8601.
Patch0:         %{name}-unbundle-iso8601.patch

BuildRequires:  check-devel
BuildRequires:  cppunit-devel
BuildRequires:  perl(ExtUtils::MakeMaker)
BuildRequires:  pkgconfig
BuildRequires:  python2-devel
BuildRequires:  python-extras
BuildRequires:  python-iso8601
BuildRequires:  python-setuptools
BuildRequires:  python-testscenarios
BuildRequires:  python-testtools >= 0.9.35

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

%package -n python-%{name}
Summary:        Streaming protocol for test results
BuildArch:      noarch
Requires:       python-extras
Requires:       python-iso8601
Requires:       python-testtools >= 0.9.35

%description -n python-%{name}
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

%package filters
Summary:        Command line filters for processing subunit streams
BuildArch:      noarch
Requires:       python-%{name} = %{version}-%{release}
Requires:       pygtk2

%description filters
Command line filters for processing subunit streams.

%prep
%setup -q
%patch0

# Remove bundled code
rm -fr python/iso8601 python/subunit/iso8601.py

# Help the dependency generator
for filt in filters/*; do
  sed 's,/usr/bin/env ,/usr/bin/,' $filt > ${filt}.new
  chmod 0755 ${filt}.new
  touch -r $filt ${filt}.new
  mv -f ${filt}.new $filt
done

# Fix underlinked library
sed "/libcppunit_subunit_la_/s,\$(LIBS),& -lcppunit -L$PWD/.libs -lsubunit," \
    -i Makefile.in

%build
export INSTALLDIRS=perl
%configure --disable-static

# Get rid of undesirable hardcoded rpaths; workaround libtool reordering
# -Wl,--as-needed after all the libraries.
sed -e 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' \
    -e 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' \
    -e 's|CC=.g..|& -Wl,--as-needed|' \
    -i libtool

make %{?_smp_mflags}

%install
%make_install INSTALL="%{_bindir}/install -p"

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

%check
export LD_LIBRARY_PATH=$PWD/.libs
export PYTHONPATH=$PWD/python/subunit:$PWD/python/subunit/tests
make check

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post cppunit -p /sbin/ldconfig

%postun cppunit -p /sbin/ldconfig

%files
%doc Apache-2.0 BSD COPYING NEWS README
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
%doc Apache-2.0 BSD COPYING
%{_bindir}/%{name}-diff
%{perl_vendorlib}/*

%files shell
%doc Apache-2.0 BSD COPYING shell/README
%config(noreplace) %{_sysconfdir}/profile.d/%{name}.sh

%files -n python-%{name}
%doc Apache-2.0 BSD COPYING
%{python2_sitelib}/%{name}/

%files filters
%{_bindir}/*
%exclude %{_bindir}/%{name}-diff

%changelog
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
