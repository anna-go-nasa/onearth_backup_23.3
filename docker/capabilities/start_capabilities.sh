#!/bin/sh
S3_URL=${1:-http://gitc-test-imagery.s3.amazonaws.com}
REDIS_HOST=${2:-127.0.0.1}
DEBUG_LOGGING=${3:-false}
S3_CONFIGS=$4

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

# Create config directories
chmod -R 755 /onearth
mkdir -p /onearth/layers
mkdir -p /etc/onearth/config/endpoint/
mkdir -p /etc/onearth/config/conf/
mkdir -p /etc/onearth/config/layers/
mkdir -p /etc/onearth/config/layers/epsg3031/best/
mkdir -p /etc/onearth/config/layers/epsg3413/best/
mkdir -p /etc/onearth/config/layers/epsg4326/best/
mkdir -p /etc/onearth/config/layers/epsg3031/std/
mkdir -p /etc/onearth/config/layers/epsg3413/std/
mkdir -p /etc/onearth/config/layers/epsg4326/std/
mkdir -p /etc/onearth/config/layers/epsg3031/nrt/
mkdir -p /etc/onearth/config/layers/epsg3413/nrt/
mkdir -p /etc/onearth/config/layers/epsg4326/nrt/

# Copy sample configs
cp ../sample_configs/conf/* /etc/onearth/config/conf/
cp ../sample_configs/endpoint/* /etc/onearth/config/endpoint/
cp -R ../sample_configs/layers/* /etc/onearth/config/layers/

# Scrape OnEarth configs from S3
if [ -z "$S3_CONFIGS" ]
then
	echo "S3_CONFIGS not set"
else
	python3.6 /usr/bin/oe_sync_s3_configs.py -f -d '/etc/onearth/config/endpoint/' -b $S3_CONFIGS -p config/endpoint >>/var/log/onearth/config.log 2>&1
	python3.6 /usr/bin/oe_sync_s3_configs.py -f -d '/etc/onearth/config/conf/' -b $S3_CONFIGS -p config/conf >>/var/log/onearth/config.log 2>&1
	python3.6 /usr/bin/oe_sync_s3_configs.py -f -d '/etc/onearth/config/layers/epsg3031/best/' -b $S3_CONFIGS -p config/layers/epsg3031/best >>/var/log/onearth/config.log 2>&1
	python3.6 /usr/bin/oe_sync_s3_configs.py -f -d '/etc/onearth/config/layers/epsg3413/best/' -b $S3_CONFIGS -p config/layers/epsg3413/best >>/var/log/onearth/config.log 2>&1
	python3.6 /usr/bin/oe_sync_s3_configs.py -f -d '/etc/onearth/config/layers/epsg4326/best/' -b $S3_CONFIGS -p config/layers/epsg4326/best >>/var/log/onearth/config.log 2>&1
	python3.6 /usr/bin/oe_sync_s3_configs.py -f -d '/etc/onearth/config/layers/epsg3031/std/' -b $S3_CONFIGS -p config/layers/epsg3031/std >>/var/log/onearth/config.log 2>&1
	python3.6 /usr/bin/oe_sync_s3_configs.py -f -d '/etc/onearth/config/layers/epsg3413/std/' -b $S3_CONFIGS -p config/layers/epsg3413/std >>/var/log/onearth/config.log 2>&1
	python3.6 /usr/bin/oe_sync_s3_configs.py -f -d '/etc/onearth/config/layers/epsg4326/std/' -b $S3_CONFIGS -p config/layers/epsg4326/std >>/var/log/onearth/config.log 2>&1
	python3.6 /usr/bin/oe_sync_s3_configs.py -f -d '/etc/onearth/config/layers/epsg3031/nrt/' -b $S3_CONFIGS -p config/layers/epsg3031/nrt >>/var/log/onearth/config.log 2>&1
	python3.6 /usr/bin/oe_sync_s3_configs.py -f -d '/etc/onearth/config/layers/epsg3413/nrt/' -b $S3_CONFIGS -p config/layers/epsg3413/nrt >>/var/log/onearth/config.log 2>&1
	python3.6 /usr/bin/oe_sync_s3_configs.py -f -d '/etc/onearth/config/layers/epsg4326/nrt/' -b $S3_CONFIGS -p config/layers/epsg4326/nrt >>/var/log/onearth/config.log 2>&1
fi

# Replace with S3 URL
sed -i 's@/{S3_URL}@'$S3_URL'@g' /etc/onearth/config/layers/*/*/*.yaml # in case there is a preceding slash
sed -i 's@/{S3_URL}@'$S3_URL'@g' /etc/onearth/config/layers/*/*.yaml # in case there is a preceding slash
sed -i 's@{S3_URL}@'$S3_URL'@g' /etc/onearth/config/layers/*/*/*.yaml
sed -i 's@{S3_URL}@'$S3_URL'@g' /etc/onearth/config/layers/*/*.yaml

# Make GC Service
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/oe-status.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/oe-status_reproject.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/profiler.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/profiler_reproject.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/epsg4326_best.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/epsg4326_std.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/epsg4326_all.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/epsg4326_nrt.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/epsg3857_best.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/epsg3857_std.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/epsg3857_all.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/epsg3857_nrt.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/epsg3031_best.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/epsg3031_std.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/epsg3031_all.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/epsg3031_nrt.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/epsg3413_best.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/epsg3413_std.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/epsg3413_all.yaml >>/var/log/onearth/config.log 2>&1
lua /home/oe2/onearth/src/modules/gc_service/make_gc_endpoint.lua /etc/onearth/config/endpoint/epsg3413_nrt.yaml >>/var/log/onearth/config.log 2>&1

# Set Apache logs to debug log level
if [ "$DEBUG_LOGGING" = true ]; then
    perl -pi -e 's/LogLevel warn/LogLevel debug/g' /etc/httpd/conf/httpd.conf
    perl -pi -e 's/LogFormat "%h %l %u %t \\"%r\\" %>s %b/LogFormat "%h %l %u %t \\"%r\\" %>s %b %D/g' /etc/httpd/conf/httpd.conf
fi

echo 'Starting Apache server'
/usr/sbin/httpd -k start
sleep 2

# Run logrotate daily at 1am
echo "0 1 * * * /etc/cron.daily/logrotate" >> /etc/crontab

# Start cron
supercronic -debug /etc/crontab > /var/log/cron_jobs.log 2>&1 &

# Tail the logs
exec tail -qFn 10000 \
 /var/log/cron_jobs.log \
  /var/log/onearth/config.log \
  /etc/httpd/logs/access.log \
  /etc/httpd/logs/error.log \
  /etc/httpd/logs/access_log \
  /etc/httpd/logs/error_log