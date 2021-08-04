## OnEarth Layer Configurator

This is a set of tools used to configure imagery layers for the OnEarth server.

## oe_configure_layer.py

The OnEarth Layer Configuration Tool (oe_configure_layer.py) is a Python script that streamlines MRF layer configuration for OnEarth services. It enables the automatic generation of server files (e.g., GetCapabilities.xml).

- The tool generates getCapabilities.xml and the server cache configuration file for WMTS.
- The tool generates getCapabilities.xml, getTileService.xml, and server cache configuration file for Tiled-WMS.
- The tool can optionally generate MapServer mapfiles.

```
Usage: oe_configure_layer.py --conf_file [layer_configuration_file.xml] --layer_dir [$LCDIR/layers/] --lcdir [$LCDIR] --projection_config [projection.xml] --time [ISO 8601] --restart_apache --no_xml --no_cache --no_twms --no_wmts --generate_legend --generate_links --skip_empty_tiles

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -a ARCHIVE_CONFIGURATION, --archive_config=ARCHIVE_CONFIGURATION
                        Full path of archive configuration file.  Default:
                        $LCDIR/conf/archive.xml
  -c LAYER_CONFIG_FILENAME, --conf_file=LAYER_CONFIG_FILENAME
                        Full path of a layer configuration filename.
                        May be repeated.
  -d LAYER_DIRECTORY, --layer_dir=LAYER_DIRECTORY
                        Full path of directory containing configuration files
                        for layers.  Default: $LCDIR/layers/
  -e, --skip_empty_tiles
                        Do not generate empty tiles for layers using color
                        maps in configuration.
  -g, --generate_legend
                        Generate legends for layers using color maps in
                        configuration.
  -l LCDIR, --lcdir=LCDIR
                        Full path of the OnEarth Layer Configurator
                        (layer_config) directory.  Default: $LCDIR
  -m TILEMATRIXSET_CONFIGURATION, --tilematrixset_config=TILEMATRIXSET_CONFIGURATION
                        Full path of TileMatrixSet configuration file.
                        Default: $LCDIR/conf/tilematrixsets.xml
  -n, --no_twms         Do not use configurations for Tiled-WMS
  -p PROJECTION_CONFIGURATION, --projection_config=PROJECTION_CONFIGURATION
                        Full path of projection configuration file.  Default:
                        $LCDIR/conf/projection.xml
  -r, --restart_apache  Restart the Apache server on completion (requires
                        sudo).
  -s, --send_email      Send email notification for errors and warnings.
  --email_server=EMAIL_SERVER
                        The server where email is sent from (overrides
                        configuration file value)
  --email_recipient=EMAIL_RECIPIENT
                        The recipient address for email notifications
                        (overrides configuration file value)
  --email_sender=EMAIL_SENDER
                        The sender for email notifications (overrides
                        configuration file value)
  --email_logging_level=EMAIL_LOGGING_LEVEL
                        Logging level for email notifications: ERROR, WARN, or
                        INFO.  Default: ERROR
  -t TIME, --time=TIME  ISO 8601 time(s) for specified configuration files
                        (--conf_file must be specified).
  -w, --no_wmts         Do not use configurations for WMTS.
  -x, --no_xml          Do not generate getCapabilities and getTileService
                        XML.
  -y, --generate_links  Generate default/current day links in the archive for
                        time varying layers.
  -z, --no_cache        Do not copy cache configuration files to cache
                        location.
  --create_mapfile      Create mapfile or add layer to existing mapfile.
                        Mapfile configuration options are set in the environment config files.
  --tmslimits_config    Full path of TileMatrixSetLimits definition file.
                        Default: $LCDIR/conf/tilematrixsetlimits.xml
```

The tool uses the following environment (recommended, but not required):

**$LCDIR** - this should reference the layer_config directory. The tool will default to (script_path)/../ if not specified.
This may also be specified by the -d, --layer_dir option.

The layer_config directory should contain the following directories:

- layers - location of layer configuration files
- twms - staging area for Tiled-WMS configurations
- wmts - staging area for WMTS configurations
- headers - location of MRF headers
- mapserver - location of templates for generation of mapfiles

### Creating layer configurations without source MRFs.

By default, the layer config tool uses information from the MRF specified by `<HeaderFileName>` in the layer config XML.

However, a header MRF is not necessary if certain fields are provided in the layer config XML. They are as follows:
`<Size>`, `<DataValues>`, `<PageSize>`, `<Rsets>`, and `<BoundingBox>`. Additional, optional tags are specified on the [layer config XML page](https://github.com/nasa-gibs/onearth/blob/master/doc/config_layer.md).

By default, the layer config tool will prefer tags in the layer config XML over those in the header MRF.

### Running oe_configure_layer.py

The tool can simply be run without any options. By default, the tool will configure all layers that have an existing configuration file in the $LCDIR/layers directory.

```
/usr/bin/oe_configure_layer
```

To specify a single configuration file to use, add the -c or --conf_file option:

```
oe_configure_layer -c layer_configuration_file.xml
```

To specify a directory of layer configuration files, add the -d or --layer_dir option:

```
oe_configure_layer -d layers/
```

An Apache server restart is required when a new layer is added. The tool does NOT restart the server by default. Use -r, --restart_apache to restart the server and load new layers.

```
oe_configure_layer -r
```

A send email option, used for error reporting, may be specified using the -s or --send_email option:

```
oe_configure_layer --send_email --email_server=EMAIL_SERVER --email_recipient=EMAIL_RECIPIENT --email_sender=EMAIL_SENDER
```

#### MapServer Config

The tool can also create/update mapfiles with the `--create-mapfile` option. The location of the mapfile is located in the enivironment config XML. When the mapfile specified by the environment config doesn't exist, a new one is created from a header template stored in the `$LCDIR/mapfiles` directory. Note that this option will overwrite previously existing layers in the mapfile if they have the same name as the layer that's being added.

When creating a new mapfile, the tool will look for `.header` and `.footer` files, and append them to the start and end of the mapfile if found. The location of these files is set by the `<MapfileConfigLocation>` element in the environment config file. The `"basename"` attribute of this element refers to the file prefix before the `.header` and `.footer` extension.

By default, the layer will be configured to point to the layer's MRF files on the file system. However, layers configured via oe_configure_remote_layers will use the layer's WMTS source via the GDAL TMS driver.

Note that the header/footers are only added when a new mapfile is created, not when an existing one is update.

```
oe_configure_layer -c layer_configuration_file.xml --create-mapfile
```

####Please refer to the following documents on how to properly configure layers:

- [OnEarth Configuration](../../doc/configuration.md)
- [Support Configuration Files](../../doc/config_support.md)
- [Layer Configuration Files](../../doc/config_layer.md)
- [Time Detection](../../doc/time_detection.md)

## oe_create_cache_config

This tool generates server cache configuration files from a list of MRF headers. It is used by oe_configure_layer.py.

```
OnEarth cache configuration tool
oe_create_cache_config [MODE] [OPTION]... [INPUT] [OUTPUT]
   MODE can be one of:
       h : Help (default)
       c : Configuration
       p : TiledWMSPattern



   Options:

   x : With mode c, generate XML
   b : With mode c, generate binary
       x and b are mutually exclusive

   INPUT and OUTPUT default to stdin and stdout respectively


  Options in the MRF header:
  <Raster>
       <Size> - x, y, z [1,1]
       <PageSize> - x, y and c [512,512,1]
       <Orientation> - TL or BL, only TL works
       <Compression> - [PNG]
  <Rsets>
       checks model=uniform attribute for levels
       checks scale=N attribute for powers of overviews
       <IndexFileName> Defaults to mrf basename + .idx
       <DataFileName>  Default to mrf basename + compression dependent extension
       <ZIndexFileName> Defaults to mrf basename + .zdb (only included if 'z' attribute of <Size> is < 1)
  <GeoTags>
       <BoundingBox> minx,miny,maxx,maxy [-180,-90,180,90]
  <TWMS>
       <Levels> Defaults to all
       <EmptyInfo> size,offset [0,0]
       <Pattern> One or more, enclose in <!CDATA[[ ]]>, the first one is used for pattern generation
       <Time> One or more, ISO 8601 time range for the product layer
```

## Contact

Contact us by sending an email to
[support@earthdata.nasa.gov](mailto:support@earthdata.nasa.gov)
