Name:		onearth
Version:	1.4.0
Release:	6%{?dist}
Summary:	Installation packages for OnEarth

License:	ASL 2.0+
URL:		http://earthdata.nasa.gov
Source0:	%{name}-%{version}.tar.bz2
Source1:	http://ftp.gnu.org/gnu/cgicc/cgicc-3.2.16.tar.gz
Source2:	http://download.osgeo.org/libspatialindex/spatialindex-src-1.8.5.tar.gz
%if 0%{?centos} == 7
Source3:	http://download.osgeo.org/mapserver/mapserver-7.0.1.tar.gz
%endif
%if 0%{?centos} == 8
Source3:	http://download.osgeo.org/mapserver/mapserver-7.4.3.tar.gz
%endif
Source4:    https://archive.apache.org/dist/httpd/httpd-2.4.6.tar.gz

BuildRequires:	cmake
BuildRequires:	chrpath
BuildRequires:	freetype-devel
BuildRequires:	gcc-c++
BuildRequires:	gibs-gdal-devel
BuildRequires:	httpd-devel
BuildRequires:	libpng-devel
BuildRequires:  sqlite-devel
BuildRequires:  turbojpeg-devel
BuildRequires:	python3-devel
%if 0%{?centos} == 7
Requires:	httpd = 2.4.6
%endif
%if 0%{?centos} == 8
Requires:	httpd => 2.4.37
%endif
Requires:	gibs-gdal >= 2.4.4
Requires:	gibs-gdal-apps >= 2.4.4
Requires:   sqlite
Requires:   libxml2
Requires:   mod_ssl
Requires:   turbojpeg

Obsoletes:	mod_oetwms mod_onearth mod_oems mod_oemstime

%description
Installation packages for OnEarth

%package demo
Summary:	Demonstration of OnEarth
Requires:	%{name} = %{version}-%{release}
BuildArch:	noarch

%description demo
Demonstration of OnEarth

%package vectorgen
Summary:	Vector data processing for OnEarth
Requires:	libxml2-devel
Requires:	libxslt-devel
Requires:	gibs-gdal-devel

%description vectorgen
Vector data processing for OnEarth

%package tools
Summary:    Auxiliary tools for OnEarth
Requires:	libpng-devel
Requires:	chrpath
Requires:	gcc-c++
Requires:	freetype-devel
Requires:	gibs-gdal >= 2.4.4
Requires:	gibs-gdal-apps >= 2.4.4
BuildArch:	noarch

%description tools
Auxiliary configuration tools for OnEarth including Legend Generator

%package mrfgen
Summary:	MRF generator for OnEarth
Requires:   onearth-tools
Requires:	gibs-gdal >= 2.4.4
Requires:	gibs-gdal-apps >= 2.4.4

%description mrfgen
MRF generator for OnEarth

%package config
Summary:	Layer configuration tools for OnEarth
Requires:	%{name} = %{version}-%{release}
Requires:   onearth-tools
BuildArch:	noarch

%description config
Layer configuration tools for OnEarth

%package mapserver
Summary:	Mapserver for OnEarth
Provides:	mapserver = %{version}-%{release}
%if 0%{?centos} == 7
Requires:   proj-epsg >= 4.8.0
Obsoletes:	mapserver < 7.0.1
%endif
%if 0%{?centos} == 8
Requires:   proj >= 6.3.2
Obsoletes:	mapserver < 7.4.3
%endif

%description mapserver
Mapserver package utilized by OnEarth for WMS and WFS services

%package test
Summary:	Test tools for OnEarth
Requires:   onearth
Requires:   onearth-config
Requires:   onearth-mapserver
Requires:   onearth-mrfgen
Requires:   onearth-tools
Requires:   onearth-vectorgen
Autoreq: 	0

%description test
Test tools for OnEarth

%prep
%setup -q
mkdir upstream
cp %{SOURCE1} upstream
cp %{SOURCE2} upstream
cp %{SOURCE3} upstream
cp %{SOURCE4} upstream

%build
make onearth PREFIX=%{_prefix}
cd src/mrfgen/
gcc -O3 RGBApng2Palpng.c -o RGBApng2Palpng -lpng
%if 0%{?centos} == 7
pip3 install setuptools
%endif
cd ../../build/mapserver
mkdir build
cd build
cmake \
      -DCMAKE_INSTALL_PREFIX="%{_prefix}" \
      -DWITH_GD=1 \
      -DWITH_GIF=0 \
      -DWITH_GDAL=1 \
      -DWITH_OGR=1 \
      -DWITH_GEOS=1 \
      -DWITH_CAIRO=0 \
      -DWITH_PROJ=1 \
      -DWITH_KML=1 \
      -DWITH_WMS=1 \
      -DWITH_WFS=1 \
      -DWITH_WCS=1 \
      -DWITH_SOS=1 \
      -DWITH_CLIENT_WMS=1 \
      -DWITH_CLIENT_WFS=1 \
      -DWITH_POSTGIS=0 \
      -DWITH_CURL=1 \
      -DWITH_LIBXML2=1 \
      -DWITH_PHP=0 \
      -DWITH_FRIBIDI=0 \
      -DWITH_FCGI=0 \
      -DWITH_THREAD_SAFETY=1 \
      -DWITH_PYTHON=0 \
      -DWITH_ICONV=1 \
      -DWITH_HARFBUZZ=0 \
      -DWITH_PROTOBUFC=0 \
      ..
make %{?smp_flags}

%install
rm -rf %{buildroot}
make onearth-install PREFIX=%{_prefix} DESTDIR=%{buildroot}

install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg3031
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg3031/1.0.0
ln -s %{_datadir}/onearth/apache/wmts.cgi %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg3031
ln -s %{_datadir}/onearth/empty_tiles/Blank_RGB_512.jpg %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg3031/black.jpg
ln -s %{_datadir}/onearth/empty_tiles/Blank_RGBA_512.png %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg3031/transparent.png
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg3413
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg3413/1.0.0
ln -s %{_datadir}/onearth/apache/wmts.cgi %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg3413
ln -s %{_datadir}/onearth/empty_tiles/Blank_RGB_512.jpg %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg3413/black.jpg
ln -s %{_datadir}/onearth/empty_tiles/Blank_RGBA_512.png %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg3413/transparent.png
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg3857
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg3857/1.0.0
ln -s %{_datadir}/onearth/apache/wmts.cgi %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg3857
ln -s %{_datadir}/onearth/empty_tiles/Blank_RGB_512.jpg %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg3857/black.jpg
ln -s %{_datadir}/onearth/empty_tiles/Blank_RGBA_512.png %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg3857/transparent.png
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg4326
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg4326/1.0.0
ln -s %{_datadir}/onearth/apache/wmts.cgi %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg4326
ln -s %{_datadir}/onearth/empty_tiles/Blank_RGB_512.jpg %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg4326/black.jpg
ln -s %{_datadir}/onearth/empty_tiles/Blank_RGBA_512.png %{buildroot}/%{_datadir}/onearth/demo/examples/default/wmts/epsg4326/transparent.png

install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg3031
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg3031/.lib
ln -s %{_datadir}/onearth/apache/twms.cgi %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg3031
ln -s %{_datadir}/onearth/empty_tiles/Blank_RGB_512.jpg %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg3031/black.jpg
ln -s %{_datadir}/onearth/empty_tiles/Blank_RGBA_512.png %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg3031/transparent.png
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg3413
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg3413/.lib
ln -s %{_datadir}/onearth/apache/twms.cgi %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg3413
ln -s %{_datadir}/onearth/empty_tiles/Blank_RGB_512.jpg %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg3413/black.jpg
ln -s %{_datadir}/onearth/empty_tiles/Blank_RGBA_512.png %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg3413/transparent.png
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg3857
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg3857/.lib
ln -s %{_datadir}/onearth/apache/twms.cgi %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg3857
ln -s %{_datadir}/onearth/empty_tiles/Blank_RGB_512.jpg %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg3857/black.jpg
ln -s %{_datadir}/onearth/empty_tiles/Blank_RGBA_512.png %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg3857/transparent.png
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg4326
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg4326/.lib
ln -s %{_datadir}/onearth/apache/twms.cgi %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg4326
ln -s %{_datadir}/onearth/empty_tiles/Blank_RGB_512.jpg %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg4326/black.jpg
ln -s %{_datadir}/onearth/empty_tiles/Blank_RGBA_512.png %{buildroot}/%{_datadir}/onearth/demo/examples/default/twms/epsg4326/transparent.png

install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/wms/
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/wms/epsg3031
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/wms/epsg3413
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/wms/epsg3857
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/wms/epsg4326
install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/wfs/
cp -r %{buildroot}/%{_datadir}/onearth/demo/examples/default/wms/* %{buildroot}/%{_datadir}/onearth/demo/examples/default/wfs/
ln -s %{_datadir}/onearth/apache/wms.cgi %{buildroot}/%{_datadir}/onearth/demo/examples/default/wms/epsg3031/wms.cgi
ln -s %{_datadir}/onearth/apache/wms.cgi %{buildroot}/%{_datadir}/onearth/demo/examples/default/wms/epsg3413/wms.cgi
ln -s %{_datadir}/onearth/apache/wms.cgi %{buildroot}/%{_datadir}/onearth/demo/examples/default/wms/epsg3857/wms.cgi
ln -s %{_datadir}/onearth/apache/wms.cgi %{buildroot}/%{_datadir}/onearth/demo/examples/default/wms/epsg4326/wms.cgi
ln -s %{_datadir}/onearth/apache/wfs.cgi %{buildroot}/%{_datadir}/onearth/demo/examples/default/wfs/epsg4326/wfs.cgi
ln -s %{_datadir}/onearth/apache/wfs.cgi %{buildroot}/%{_datadir}/onearth/demo/examples/default/wfs/epsg3857/wfs.cgi
ln -s %{_datadir}/onearth/apache/wfs.cgi %{buildroot}/%{_datadir}/onearth/demo/examples/default/wfs/epsg3413/wfs.cgi
ln -s %{_datadir}/onearth/apache/wfs.cgi %{buildroot}/%{_datadir}/onearth/demo/examples/default/wfs/epsg3031/wfs.cgi

install -m 755 -d %{buildroot}/%{_datadir}/onearth/demo/examples/default/lib
install -m 755 -d %{buildroot}/%{_sysconfdir}/httpd/conf.d
mv %{buildroot}/%{_datadir}/onearth/demo/examples/default/onearth-demo.conf \
   %{buildroot}/%{_sysconfdir}/httpd/conf.d
( cd build/mapserver/build; DESTDIR=%{buildroot} make install )
mv %{buildroot}/%{_libdir}/../lib/* %{buildroot}/%{_libdir}/
chrpath --delete %{buildroot}/%{_bindir}/legend
chrpath --delete %{buildroot}/%{_bindir}/mapserv
chrpath --delete %{buildroot}/%{_bindir}/msencrypt
chrpath --delete %{buildroot}/%{_bindir}/scalebar
chrpath --delete %{buildroot}/%{_bindir}/shp2img
chrpath --delete %{buildroot}/%{_bindir}/shptree
chrpath --delete %{buildroot}/%{_bindir}/shptreetst
chrpath --delete %{buildroot}/%{_bindir}/shptreevis
chrpath --delete %{buildroot}/%{_bindir}/sortshp
chrpath --delete %{buildroot}/%{_bindir}/tile4ms
chrpath --delete %{buildroot}/%{_libdir}/*.so
rm -rf %{buildroot}/%{_datarootdir}/mapserver/cmake/

%clean
rm -rf %{buildroot}

%files
%{_libdir}/httpd/modules/*
%defattr(-,gibs,gibs,775)
%dir %{_datadir}/onearth
%defattr(775,gibs,gibs,775)
%{_datadir}/onearth/apache
%{_datadir}/onearth/empty_tiles
%defattr(755,root,root,755)
%{_bindir}/oe_create_cache_config
%{_datadir}/cgicc

%post
cd %{_datadir}/cgicc/
%{_datadir}/cgicc/configure --prefix=%{_prefix} --libdir=%{_libdir}
make install
/sbin/ldconfig

cd %{_libdir}/httpd/modules/
for file in %{_libdir}/httpd/modules/mod_proxy/*.so; do
	mv "`basename "$file"`" "`basename "$file" .so`.save"
	ln -s "$file" `basename "$file"`
done

%postun
cd %{_libdir}/httpd/modules/
for file in %{_libdir}/httpd/modules/*.save; do
	mv "$file" "`basename "$file" .save`.so"
done

%files tools
%defattr(755,root,root,-)
%{_bindir}/oe_generate_legend.py
%{_bindir}/oe_generate_empty_tile.py
%{_bindir}/oe_utils.py
%{_bindir}/twmsbox2wmts.py
%{_bindir}/wmts2twmsbox.py
%{_bindir}/read_idx.py
%{_bindir}/read_mrf.py
%{_bindir}/read_mrfdata.py
%{_bindir}/colorMaptoHTML.py
%{_bindir}/colorMaptoSLD.py
%{_bindir}/SLDtoColorMap.py

%files config
%defattr(664,gibs,gibs,775)
%{_sysconfdir}/onearth/config/
%config(noreplace) %{_sysconfdir}/onearth/config/conf
%config(noreplace) %{_sysconfdir}/onearth/config/layers
%config(noreplace) %{_sysconfdir}/onearth/config/reproject
%config(noreplace) %{_sysconfdir}/onearth/config/headers
%config(noreplace) %{_sysconfdir}/onearth/config/mapserver
%{_sysconfdir}/onearth/config/schema
%defattr(755,root,root,-)
%{_bindir}/oe_configure_layer
%{_bindir}/oe_configure_reproject_layer.py
%{_bindir}/oe_configure_remote_layers.py
%{_bindir}/oe_validate_configs.py

%files mrfgen
%defattr(664,gibs,gibs,775)
%{_datadir}/onearth/mrfgen
%defattr(755,root,root,-)
%{_bindir}/RGBApng2Palpng
%{_bindir}/mrfgen
%{_bindir}/colormap2vrt.py
%{_bindir}/overtiffpacker.py
%{_bindir}/oe_validate_palette.py

%files demo
%defattr(-,gibs,gibs,-)
%{_datadir}/onearth/demo
%config(noreplace) %{_sysconfdir}/httpd/conf.d/onearth-demo.conf

%post demo
sed -i 's/#Require/Require/g' /etc/httpd/conf.d/onearth-demo.conf
cd %{_datadir}/onearth/apache/kml
make WEB_HOST=localhost/onearth/twms/epsg4326
mv %{_datadir}/onearth/apache/kml/kmlgen.cgi \
   %{_datadir}/onearth/demo/examples/default/twms/epsg4326
ln -s %{_datadir}/onearth/demo/html_lib/* %{_datadir}/onearth/demo/examples/default/lib/

%postun demo
rm %{_datadir}/onearth/demo/examples/default/lib/*
if [ -f /etc/httpd/conf.d/reproject-demo.conf ]; then rm /etc/httpd/conf.d/reproject-demo.conf; fi

%files mapserver
%defattr(755,root,root,755)
%{_libdir}/libmapserver.so*
%{_includedir}/mapserver/*

%{_bindir}/legend
%{_bindir}/mapserv
%{_bindir}/msencrypt
%{_bindir}/scalebar
%{_bindir}/shp2img
%{_bindir}/shptree
%{_bindir}/shptreetst
%{_bindir}/shptreevis
%{_bindir}/sortshp
%{_bindir}/tile4ms

%files vectorgen
%defattr(755,root,root,755)
%{_datadir}/onearth/vectorgen
%{_libdir}/libspatialindex*
%{_libdir}/pkgconfig/libspatialindex.pc
%{_includedir}/spatialindex/*
%{_bindir}/oe_vectorgen
%{_bindir}/oe_create_mvt_mrf.py

%post tools
sed -i 's@\/usr\/libexec\/platform-python@\/usr\/bin\/env python3@g' /usr/bin/oe_*.py /usr/bin/twmsbox2wmts.py /usr/bin/wmts2twmsbox.py /usr/bin/read_*.py /usr/bin/colorMap*.py /usr/bin/SLDtoColorMap.py

%post config
sed -i 's@\/usr\/libexec\/platform-python@\/usr\/bin\/env python3@g' /usr/bin/oe_*.py

%post mrfgen
sed -i 's@\/usr\/libexec\/platform-python@\/usr\/bin\/env python3@g' /usr/bin/mrfgen /usr/bin/colormap2vrt.py /usr/bin/overtiffpacker.py /usr/bin/oe_validate_palette.py

%post vectorgen
/sbin/ldconfig
sed -i 's@\/usr\/libexec\/platform-python@\/usr\/bin\/env python3@g' /usr/bin/oe_vectorgen /usr/bin/oe_create_mvt_mrf.py

%files test
%defattr(-,gibs,gibs,-)
%{_datadir}/onearth/test

%post test
pip3 install unittest2 unittest-xml-reporting==1.14.0 requests

%changelog
* Mon Apr 05 2021 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 1.4.0-4
- Support for CentOS 8 builds

* Mon Nov 09 2020 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 1.4.0-3
- Use pip3 and removed old Python dependencies

* Mon Jul 17 2017 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 1.3.1-3
- Added test package and cleaned up demo

* Fri Jul 07 2017 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 1.3.1-2
- Updated demo package; added pyparsing and parse_apache_configs install to post config

* Tue Jun 13 2017 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 1.3.1-1
- Added python xml install to post config

* Thu Nov 03 2016 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 1.1.2-1
- Added onearth-tools package and reorganized files for several packages

* Wed Aug 17 2016 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 1.1.0-1
- Added onearth-mapserver package, mod_oems, and mod_oemstime

* Wed Aug 17 2016 Joshua D. Rodriguez <joshua.d.rodriguez@jpl.nasa.gov> - 1.0.3
- Added vectorgen package

* Fri Jul 15 2016 Joshua D. Rodriguez <joshua.d.rodriguez@jpl.nasa.gov> - 1.0.2-1
- Updated Matplotlib dependency install to 1.5.1

* Wed May 25 2016 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 1.0.1-1
- Modified empty tiles

* Tue Mar 8 2016 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 0.9.1-1
- Removed numpy as it is included in gibs-gdal

* Wed Nov 11 2015 Joshua Rodriguez <joshua.d.rodriguez@jpl.nasa.gov> - 0.8.0-1
- Added creation of kml/twms endpoint

* Wed Nov 4 2015 Joshua Rodriguez <joshua.d.rodriguez@jpl.nasa.gov> - 0.8.0-1
- Remove Postgres dependencies

* Mon Aug 10 2015 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 0.7.0-1
- Added requires for sqlite

* Tue Mar 24 2015 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 0.6.3-2
- Added installation of cgicc for kmlgen

* Thu Feb 12 2015 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 0.6.3-1
- Updated BuildRequires and config package Requires

* Thu Jan 29 2015 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 0.6.2-1
- Updated dependencies including downloads for numpy and matplotlib

* Mon Nov 24 2014 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 0.6.1-1
- Added oe_generate_empty_tile and missing python dependencies

* Fri Oct 03 2014 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 0.5.0-1
- Removed deprecated OnEarth layer configuration files and folders

* Mon Aug 18 2014 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 0.4.2-1
- Reorganized into separate packages for different components

* Fri Aug 8 2014 Mike McGann <mike.mcgann@nasa.gov> - 0.4.1-2
- Updates for building on EL7

* Mon Jul 28 2014 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 0.4.1-1
- Added noreplace options to configuration directories

* Wed May 14 2014 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 0.3.2-1
- Renamed mod_onearth directory to onearth and added TWMS directories

* Wed Apr 30 2014 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 0.3.1-1
- Changed the version to 0.3.1

* Fri Apr 4 2014 Mike McGann <mike.mcgann@nasa.gov> - 0.3.0-2
- Included layer_config in package

* Tue Apr 1 2014 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 0.3.0-1
- Changed the version to 0.3.0

* Wed Feb 26 2014 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 0.2.5-1
- Changed the version to 0.2.5

* Tue Feb 18 2014 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 0.2.4-1
- Changed the version to 0.2.4 to be consistent with project release

* Thu Feb 13 2014 Joe T. Roberts <joe.t.roberts@jpl.nasa.gov> - 0.0.0-2
- Changed to release 0.2

* Wed Sep 4 2013 Mike McGann <mike.mcgann@nasa.gov> - 0.0.0-1
- Initial package
