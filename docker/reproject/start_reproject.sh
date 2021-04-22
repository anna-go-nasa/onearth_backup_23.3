#!/bin/sh
DEBUG_LOGGING=${1:-false}
S3_CONFIGS=$2

if [ ! -f /.dockerenv ]; then
  echo "This script is only intended to be run from within Docker" >&2
  exit 1
fi

cd /home/oe2/onearth/docker/reproject

# Load test layers
mkdir -p /var/www/html/reproject_endpoint/date_test/default/tms
cp oe2_test_mod_reproject_date.conf /etc/httpd/conf.d
cp ../layer_configs/oe2_test_mod_reproject_layer_source*.config /var/www/html/reproject_endpoint/date_test/default/tms/oe2_test_mod_reproject_date_layer_source.config
cp ../layer_configs/oe2_test_mod_reproject_date*.config /var/www/html/reproject_endpoint/date_test/default/tms/

mkdir -p /var/www/html/reproject_endpoint/static_test/default/tms
cp oe2_test_mod_reproject_static.conf /etc/httpd/conf.d
cp ../layer_configs/oe2_test_mod_reproject_layer_source*.config /var/www/html/reproject_endpoint/static_test/default/tms/oe2_test_mod_reproject_static_layer_source.config
cp ../layer_configs/oe2_test_mod_reproject_static*.config /var/www/html/reproject_endpoint/static_test/default/tms/

# WMTS endpoints
mkdir -p /var/www/html/oe-status_reproject/
mkdir -p /var/www/html/wmts/epsg3857/all
mkdir -p /var/www/html/wmts/epsg3857/best
mkdir -p /var/www/html/wmts/epsg3857/std
mkdir -p /var/www/html/wmts/epsg3857/nrt

# TWMS endpoints
mkdir -p /var/www/html/twms/epsg3857/all
mkdir -p /var/www/html/twms/epsg3857/best
mkdir -p /var/www/html/twms/epsg3857/std
mkdir -p /var/www/html/twms/epsg3857/nrt

# Create config directories
mkdir -p /onearth
chmod -R 755 /onearth
mkdir -p /etc/onearth/config/endpoint/
mkdir -p /etc/onearth/config/conf/

# Copy sample configs
cp ../sample_configs/conf/* /etc/onearth/config/conf/
cp ../sample_configs/endpoint/* /etc/onearth/config/endpoint/

# Scrape OnEarth configs from S3
if [ -z "$S3_CONFIGS" ]
then
	echo "S3_CONFIGS not set"
else
	python3.6 /usr/bin/oe_sync_s3_configs.py -f -d '/etc/onearth/config/endpoint/' -b $S3_CONFIGS -p config/endpoint >>/var/log/onearth/config.log 2>&1
	python3.6 /usr/bin/oe_sync_s3_configs.py -f -d '/etc/onearth/config/conf/' -b $S3_CONFIGS -p config/conf >>/var/log/onearth/config.log 2>&1
fi

# Copy tilematrixsets config file
cp /home/oe2/onearth/src/modules/mod_wmts_wrapper/configure_tool/tilematrixsets.xml /etc/onearth/config/conf/

# Run reproject config tools
sleep 10
python3.6 /usr/bin/oe2_reproject_configure.py /etc/onearth/config/endpoint/oe-status_reproject.yaml >>/var/log/onearth/config.log 2>&1

# Set Apache logs to debug log level
if [ "$DEBUG_LOGGING" = true ]; then
    perl -pi -e 's/LogLevel warn/LogLevel debug/g' /etc/httpd/conf/httpd.conf
    perl -pi -e 's/LogFormat "%h %l %u %t \\"%r\\" %>s %b/LogFormat "%h %l %u %t \\"%r\\" %>s %b %D/g' /etc/httpd/conf/httpd.conf
fi

# Setup Apache extended server status
cat >> /etc/httpd/conf/httpd.conf <<EOS
LoadModule status_module modules/mod_status.so

<Location /server-status>
   SetHandler server-status
   Allow from all 
</Location>

# ExtendedStatus controls whether Apache will generate "full" status
# information (ExtendedStatus On) or just basic information (ExtendedStatus
# Off) when the "server-status" handler is called. The default is Off.
#
ExtendedStatus On
EOS

echo 'Starting Apache server'
/usr/sbin/httpd -k restart
sleep 2

# Load additional endpoints
echo 'Loading additional endpoints'
python3.6 /usr/bin/oe2_reproject_configure.py /etc/onearth/config/endpoint/epsg3857_best.yaml >>/var/log/onearth/config.log 2>&1
python3.6 /usr/bin/oe2_reproject_configure.py /etc/onearth/config/endpoint/epsg3857_std.yaml >>/var/log/onearth/config.log 2>&1
python3.6 /usr/bin/oe2_reproject_configure.py /etc/onearth/config/endpoint/epsg3857_all.yaml >>/var/log/onearth/config.log 2>&1
python3.6 /usr/bin/oe2_reproject_configure.py /etc/onearth/config/endpoint/epsg3857_nrt.yaml >>/var/log/onearth/config.log 2>&1

echo 'Restarting Apache server'
/usr/sbin/httpd -k restart
sleep 2

# Run logrotate hourly
echo "0 * * * * /etc/cron.hourly/logrotate" >> /etc/crontab

# Start cron
supercronic -debug /etc/crontab > /var/log/cron_jobs.log 2>&1 &

# Tail the logs
exec tail -qFn 10000 \
  /var/log/cron_jobs.log \
  /var/log/onearth/config.log \
  /etc/httpd/logs/access_log \
  /etc/httpd/logs/error_log