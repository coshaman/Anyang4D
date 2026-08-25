# Goal 2 visual review

Reviewed the required viewport matrix and representative screenshots on 2026-08-20:

- `goal2-390x844.png`: mobile hierarchy is readable; status, search, category controls, map, facility list, 119 guidance, and data link fit in a single vertical flow.
- `goal2-1280x720.png`: map-first desktop layout preserves a large map and a separate nearby-facility/support column without dashboard-card clutter.
- `goal2-200-percent-phone.png`: enlarged controls and text remain usable; the category row was changed to wrap so AED is not clipped at 200% zoom.

The local browser sandbox could not fetch `tile.openstreetmap.org`, so captured map surfaces show the neutral map background and controls rather than live raster tiles. Production code still requests the real OSM tile URL, shows OSM attribution, and does not cache tiles offline.
