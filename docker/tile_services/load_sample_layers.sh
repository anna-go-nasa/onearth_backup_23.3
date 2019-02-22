#!/bin/sh
S3_URL=${1:-http://gitc-test-imagery.s3.amazonaws.com}
REDIS_HOST=${2:-127.0.0.1}

if [ ! -f /.dockerenv ]; then
  echo "This script is only intended to be run from within Docker" >&2
  exit 1
fi

# WMTS endpoints
mkdir -p /var/www/html/oe-status/
mkdir -p /var/www/html/oe-status_reproject/
mkdir -p /var/www/html/profiler/
mkdir -p /var/www/html/profiler_reproject/
mkdir -p /var/www/html/wmts/epsg4326/all
mkdir -p /var/www/html/wmts/epsg4326/best
mkdir -p /var/www/html/wmts/epsg4326/std
mkdir -p /var/www/html/wmts/epsg4326/nrt
mkdir -p /var/www/html/wmts/epsg3857/all
mkdir -p /var/www/html/wmts/epsg3857/best
mkdir -p /var/www/html/wmts/epsg3857/std
mkdir -p /var/www/html/wmts/epsg3857/nrt
mkdir -p /var/www/html/wmts/epsg3031/all
mkdir -p /var/www/html/wmts/epsg3031/best
mkdir -p /var/www/html/wmts/epsg3031/std
mkdir -p /var/www/html/wmts/epsg3031/nrt
mkdir -p /var/www/html/wmts/epsg3413/all
mkdir -p /var/www/html/wmts/epsg3413/best
mkdir -p /var/www/html/wmts/epsg3413/std
mkdir -p /var/www/html/wmts/epsg3413/nrt

# TWMS endpoints
mkdir -p /var/www/html/twms/epsg4326/all
mkdir -p /var/www/html/twms/epsg4326/best
mkdir -p /var/www/html/twms/epsg4326/std
mkdir -p /var/www/html/twms/epsg4326/nrt
mkdir -p /var/www/html/twms/epsg3857/all
mkdir -p /var/www/html/twms/epsg3857/best
mkdir -p /var/www/html/twms/epsg3857/std
mkdir -p /var/www/html/twms/epsg3857/nrt
mkdir -p /var/www/html/twms/epsg3031/all
mkdir -p /var/www/html/twms/epsg3031/best
mkdir -p /var/www/html/twms/epsg3031/std
mkdir -p /var/www/html/twms/epsg3031/nrt
mkdir -p /var/www/html/twms/epsg3413/all
mkdir -p /var/www/html/twms/epsg3413/best
mkdir -p /var/www/html/twms/epsg3413/std
mkdir -p /var/www/html/twms/epsg3413/nrt

# Copy empty tiles
mkdir -p /onearth/empty_tiles/
cp ../empty_tiles/* /onearth/empty_tiles/

# Copy sample configs
chmod -R 755 /onearth
mkdir -p /onearth/layers
mkdir -p /etc/onearth/config/endpoint/
mkdir -p /etc/onearth/config/layers/
cp ../sample_configs/endpoint/* /etc/onearth/config/endpoint/
cp -R ../sample_configs/layers/* /etc/onearth/config/layers/
# Replace with S3 URL
sed -i 's@{S3_URL}@'$S3_URL'@g' /etc/onearth/config/layers/*/*/*.yaml
sed -i 's@{S3_URL}@'$S3_URL'@g' /etc/onearth/config/layers/*/*.yaml

echo 'Starting Apache server'
/usr/sbin/httpd -k start
sleep 2

# Run layer config tools
python3.6 /usr/bin/oe2_wmts_configure.py /etc/onearth/config/endpoint/oe-status.yaml
python3.6 /usr/bin/oe2_wmts_configure.py /etc/onearth/config/endpoint/profiler.yaml
python3.6 /usr/bin/oe2_wmts_configure.py /etc/onearth/config/endpoint/epsg4326_best.yaml
python3.6 /usr/bin/oe2_wmts_configure.py /etc/onearth/config/endpoint/epsg4326_std.yaml
python3.6 /usr/bin/oe2_wmts_configure.py /etc/onearth/config/endpoint/epsg4326_all.yaml
python3.6 /usr/bin/oe2_wmts_configure.py /etc/onearth/config/endpoint/epsg3031_best.yaml
python3.6 /usr/bin/oe2_wmts_configure.py /etc/onearth/config/endpoint/epsg3031_std.yaml
python3.6 /usr/bin/oe2_wmts_configure.py /etc/onearth/config/endpoint/epsg3031_all.yaml
python3.6 /usr/bin/oe2_wmts_configure.py /etc/onearth/config/endpoint/epsg3413_best.yaml
python3.6 /usr/bin/oe2_wmts_configure.py /etc/onearth/config/endpoint/epsg3413_std.yaml
python3.6 /usr/bin/oe2_wmts_configure.py /etc/onearth/config/endpoint/epsg3413_all.yaml

echo 'Starting Apache server'
/usr/sbin/httpd -k start
sleep 2

# Data for oe-status
cp oe2_status.conf /etc/httpd/conf.d
mkdir -p /onearth/idx/oe-status/BlueMarble16km
cp ../test_imagery/*BlueMarble16km* /onearth/idx/oe-status/BlueMarble16km/

# Performance Test Data

mkdir -p /onearth/idx/profiler/BlueMarble
wget -O /onearth/idx/profiler/BlueMarble/BlueMarble.idx https://s3.amazonaws.com/gitc-test-imagery/BlueMarble.idx

mkdir -p /onearth/idx/profiler/MOGCR_LQD_143_STD
f=$(../src/test/oe_gen_hash_filename.py -l MOGCR_LQD_143_STD -t 1293840000 -e .idx)
wget -O /onearth/idx/profiler/MOGCR_LQD_143_STD/$f https://s3.amazonaws.com/gitc-test-imagery/$f

mkdir -p /onearth/idx/profiler/VNGCR_LQD_I1-M4-M3_NRT
wget -O /onearth/idx/profiler/VNGCR_LQD_I1-M4-M3_NRT/VNGCR_LQD_I1-M4-M3_NRT.idx https://s3.amazonaws.com/gitc-test-imagery/VNGCR_LQD_I1-M4-M3_NRT.idx
d=1516060800
until [ $d -gt 1524614400 ]; do
    f=$(../src/test/oe_gen_hash_filename.py -l VNGCR_LQD_I1-M4-M3_NRT -t $d -e .idx)
    ln -s /onearth/idx/profiler/VNGCR_LQD_I1-M4-M3_NRT/VNGCR_LQD_I1-M4-M3_NRT.idx /onearth/idx/profiler/VNGCR_LQD_I1-M4-M3_NRT/$f
    let d+=86400
done

mkdir -p /onearth/idx/profiler/MOG13Q4_LQD_NDVI_NRT
wget -O /onearth/idx/profiler/MOG13Q4_LQD_NDVI_NRT/MOG13Q4_LQD_NDVI_NRT.idx https://s3.amazonaws.com/gitc-test-imagery/MOG13Q4_LQD_NDVI_NRT.idx
d=1514764800
until [ $d -gt 1523318400 ]; do
    f=$(../src/test/oe_gen_hash_filename.py -l MOG13Q4_LQD_NDVI_NRT -t $d -e .idx)
    ln -s /onearth/idx/profiler/MOG13Q4_LQD_NDVI_NRT/MOG13Q4_LQD_NDVI_NRT.idx /onearth/idx/profiler/MOG13Q4_LQD_NDVI_NRT/$f
    let d+=86400
done

# ASTER_L1T_Radiance_Terrain_Corrected subdaily example

mkdir -p /onearth/idx/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/1970
mkdir -p /onearth/idx/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/2016
wget -O /onearth/idx/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/2016/4642-ASTER_L1T_Radiance_Terrain_Corrected-2016336011844.idx.tgz https://s3.amazonaws.com/gitc-test-imagery/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/2016/4642-ASTER_L1T_Radiance_Terrain_Corrected-2016336011844.idx.tgz
tar -zxf /onearth/idx/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/2016/4642-ASTER_L1T_Radiance_Terrain_Corrected-2016336011844.idx.tgz -C /onearth/idx/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/2016/
mv /onearth/idx/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/2016/out/out.idx /onearth/idx/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/2016/4642-ASTER_L1T_Radiance_Terrain_Corrected-2016336011844.idx
wget -O /onearth/idx/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/2016/5978-ASTER_L1T_Radiance_Terrain_Corrected-2016336011835.idx.tgz https://s3.amazonaws.com/gitc-test-imagery/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/2016/5978-ASTER_L1T_Radiance_Terrain_Corrected-2016336011835.idx.tgz
tar -zxf /onearth/idx/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/2016/5978-ASTER_L1T_Radiance_Terrain_Corrected-2016336011835.idx.tgz -C /onearth/idx/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/2016/
mv /onearth/idx/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/2016/out/out.idx /onearth/idx/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/2016/5978-ASTER_L1T_Radiance_Terrain_Corrected-2016336011835.idx
wget -O /onearth/idx/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/1970/3b5c-ASTER_L1T_Radiance_Terrain_Corrected-1970001000000.idx.tgz https://s3.amazonaws.com/gitc-test-imagery/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/1970/3b5c-ASTER_L1T_Radiance_Terrain_Corrected-1970001000000.idx.tgz
tar -zxf /onearth/idx/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/1970/3b5c-ASTER_L1T_Radiance_Terrain_Corrected-1970001000000.idx.tgz -C /onearth/idx/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/1970/
mv /onearth/idx/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/1970/out/out.idx /onearth/idx/epsg4326/ASTER_L1T_Radiance_Terrain_Corrected/1970/3b5c-ASTER_L1T_Radiance_Terrain_Corrected-1970001000000.idx

# Start Redis if running locally
if [ "$REDIS_HOST" = "127.0.0.1" ]; then
	echo 'Starting Redis server'
	/usr/bin/redis-server &
	sleep 2
	# Turn off the following line for production systems
	/usr/bin/redis-cli -n 0 CONFIG SET protected-mode no
fi

# Add time metadata to Redis
/usr/bin/redis-cli -h $REDIS_HOST -n 0 DEL layer:date_test
/usr/bin/redis-cli -h $REDIS_HOST -n 0 SET layer:date_test:default "2015-01-01"
/usr/bin/redis-cli -h $REDIS_HOST -n 0 SADD layer:date_test:periods "2015-01-01/2017-01-01/P1Y"
/usr/bin/redis-cli -h $REDIS_HOST -n 0 DEL layer:date_test_year_dir
/usr/bin/redis-cli -h $REDIS_HOST -n 0 SET layer:date_test_year_dir:default "2015-01-01"
/usr/bin/redis-cli -h $REDIS_HOST -n 0 SADD layer:date_test_year_dir:periods "2015-01-01/2017-01-01/P1Y"
/usr/bin/redis-cli -h $REDIS_HOST -n 0 DEL layer:BlueMarble16km
/usr/bin/redis-cli -h $REDIS_HOST -n 0 SET layer:BlueMarble16km:default "2004-08-01"
/usr/bin/redis-cli -h $REDIS_HOST -n 0 SADD layer:BlueMarble16km:periods "2004-08-01/2004-08-01/P1M"


echo 'Restarting Apache server'
/usr/sbin/httpd -k restart
sleep 2