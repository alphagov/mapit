# About datasets

## ONSI Datasets

OSNI releases can be found via their Spatial NI site at
<http://osni.spatial-ni.opendata.arcgis.com/>. Note that they
don't have a single download and you have to fetch each dataset
we want individually. We're looking for the latest releases from
the OSNI Open Data Largescale Boundaries of the following:
- [Wards 2012](http://osni-spatial-ni.opendata.arcgis.com/datasets/55cd419b2d2144de9565c9b8f73a226d_0)
- [District Electoral Areas 2012](http://osni-spatial-ni.opendata.arcgis.com/datasets/981a83027c0e4790891baadcfaa359a3_4)
- [Local Government Districts 2012](http://osni-spatial-ni.opendata.arcgis.com/datasets/a55726475f1b460c927d1816ffde6c72_2)
- [Parliamentary Constituencies 2008](http://osni-spatial-ni.opendata.arcgis.com/datasets/563dc2ec3d9943428e3fe68966d40deb_3)
- [NI Outline](http://osni-spatial-ni.opendata.arcgis.com/datasets/d9dfdaf77847401e81efc9471dcd09e1_0)
If the boundaries are redrawn the name of the dataset may change to
reflect the year of the legislation (e.g. there are Wards 1993 and
Wards 2012 datasets at the moment, future legislation may introduce a
Wards 2020 dataset).

**Note:** the package of OSNI data that is mirrored on [mysociety's
cache](http://parlvid.mysociety.org/os/) is currently a `.tar.gz` that
contains all the all 5 shapefile downloads and a `metadata.json` file
describing the source, release date, SRID and type.
You should check that any new package has the same structure and if not,
update `import-uk-onspd` accordingly.
If you have to download your own copies of the OSNI data you should check
the shapefiles have the correct SRID because they may change from the
defaults. If they are incorrect the point lookup can fail (finding parents)
or give incorrect results (postcodes).

Use [`ogrinfo`](http://www.gdal.org/ogrinfo.html) to get the SRID of
a shapefile:
```
$ ogrinfo OSNI_Open_Data_Largescale_Boundaries__Parliamentary_Constituencies_2008.shp OSNI_Open_Data_Largescale_Boundaries__Parliamentary_Constituencies_2008 -so
```

Look up the `GEOGCS` field on [this coordinate systems page](http://downloads.esri.com/support/documentation/ims_/Support_files/elements/pcs.htm)
to find the SRID. Most likely SRIDs are 29902 (the NI  projection),
29900 (the UK projection), 4326 (the web mercator projection used
by google earth among others).
