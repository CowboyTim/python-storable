#...CentOS 6 compatibility for delivering license file
%{!?_licensedir: %global license %%doc}
%{!?_licensedir: %global _licensedir %%_docdir}

# python sitelib doublecheck
%{!?python_sitelib: %global python_sitelib /usr/lib/python3/dist-packages}

%define __find_provides %{nil} 
%define __find_requires %{nil} 
%define _use_internal_dependency_generator 0
%define python_sitelib /usr/lib/python3/dist-packages

Summary: Python module that is able to read Perl storable data.
Name: python-storable
Version: %{version}

Release: 1%{?dist}

License: zlib/libpng
Group: Development/Libraries

#From:  https://github.com/CowboyTim/python-storable
Source0:  storable-%{version}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}
BuildArch: noarch
Autoprov: 0
Autoreq: 0
Provides: %{name} = %{version}-%{release}, %{name}
Requires: python

%description
This is a Python module that is able to read Perl storable files. Storable is a nice and efficient binary format for Perl that is very popular. A lot of other serialization/deserialization modules exist that are even more or less standardized: JSON, XML, CSV,.. etc. Storable is more or less Perl specific.

To ease integration between Perl - where storable sometimes is the only option - and Python this module is a bridge.

%prep
%setup -c %{name}-%{version}
mv $RPM_BUILD_DIR/%{name}-%{version}/storable-%{version} $RPM_BUILD_DIR/%{name}-%{version}/tmp

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_licensedir}
install $RPM_BUILD_DIR/%{name}-%{version}/tmp/LICENSE.txt $RPM_BUILD_ROOT%{_licensedir}/python-storable-LICENSE.txt
mkdir -p $RPM_BUILD_ROOT%{python_sitelib}
mv -f tmp/storable $RPM_BUILD_ROOT%{python_sitelib}/storable
mv -f tmp/storable.egg-info $RPM_BUILD_ROOT%{python_sitelib}/storable-%{version}.egg-info

%clean
rm -rf $RPM_BUILD_ROOT
rm -rf $RPM_BUILD_DIR

%files
%license %{_licensedir}/python-storable-LICENSE.txt
%defattr(-,root,root)
%{python_sitelib}/storable
%{python_sitelib}/storable-%{version}.egg-info

%changelog
* Sat Oct 02 2021 Tim Aerts <aardbeiplantje@gmail.com> 1.2.4-1
- Updated this rpm spec file for version 1.2.4
- Enable travis CI integration with travis-ci.com
- Enable github Actions integration with pupi.org
- Fix utf8 guessing
- Add Storable 3.15 tests
* Sat Oct 03 2020 Rich Johnson <richard.johnson@stratus.com> 1.1.0-1
- Packaging of earlier work by Tim Aerts <aardbeiplantje@gmail.com>
