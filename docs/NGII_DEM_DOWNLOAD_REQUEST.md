# NGII DEM download request — compact Anyang demo (2020+ only)

Download current 2020-or-newer native 1m or 5m records covering the AOI in `docs/DEMO_AOI.md`:

| Target sheets | Native grid | Production/build year | Required evidence |
| --- | --- | --- | --- |
| 37612048, 37612049, 37612058, 37612059 | exactly 1m X 1m or 5m X 5m | 2020 or newer | provider receipt, checksum, CRS/vertical datum, nodata, tile boundaries |

The four 2009 1m records formerly listed in this document are historical reference metadata only and do not satisfy the user’s 2020+ requirement. Do not download or promote them as the current source. Do not substitute the supplied duplicate native-90m HFA raster or an interpolated display grid.

The target local directory is `data/raw/ngii/demo_aoi_highres/`. Preserve original files and sidecars. Do not request all 101 Anyang sheets.

Reason: a native 2020+ 1m/5m source is required before the frozen terrain validation gate can consider a real Anyang Level-A scenario. Even after Level-A approval, this would not authorize Level-B/C depth claims or citizen routing.

Current status: `HUMAN_ACTION_REQUIRED` through the NGII portal’s authenticated large-file download workflow. See `docs/NGII_1M_EXACT_DOWNLOAD_CHECKLIST.md`.
