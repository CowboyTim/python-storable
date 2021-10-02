#...CentOS 6 compatibility for delivering license file
%{!?_licensedir: %global license %%doc}
%{!?_licensedir: %global _licensedir %%_docdir}

Summary: Python module that is able to read Perl storable data.
Name: python-storable
Version: 1.1.0

Release: 1%{?dist}

License: zlib/libpng
Group: Development/Libraries

#From:  https://github.com/CowboyTim/python-storable
Source0:  python-storable_%{version}.tar

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}
BuildArch: noarch
BuildRequires: python-setuptools
BuildRequires: python2-devel

%description
This is a Python module that is able to read Perl storable files. Storable is a nice and efficient binary format for Perl that is very popular. A lot of other serialization/deserialization modules exist that are even more or less standardized: JSON, XML, CSV,.. etc. Storable is more or less Perl specific.

To ease integration between Perl - where storable sometimes is the only option - and Python this module is a bridge.

%prep
%setup -c %{name}-%{version}

%build

%install
mkdir -p $RPM_BUILD_ROOT%{_licensedir}
install LICENSE.txt $RPM_BUILD_ROOT%{_licensedir}/python-storable-LICENSE.txt
mkdir -p $RPM_BUILD_ROOT%{python_sitelib}
cp -ar storable $RPM_BUILD_ROOT%{python_sitelib}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%license %{_licensedir}/python-storable-LICENSE.txt
%defattr(-,root,root)
%{python_sitelib}/storable

%changelog
* Sat Oct 03 2020 Rich Johnson <richard.johnson@stratus.com> 1.1.0-1
- Packaging of earlier work by Tim Aerts <aardbeiplantje@gmail.com>
