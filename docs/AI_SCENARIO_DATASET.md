# AI scenario dataset

The Goal 5A corpus contains reproducible `SIMULATED_ADMIN_SCENARIO` combinations over the real bounded OSM graph, official municipal population totals, and the same canonical national-filtered shelter facilities used by Goal 4B. It covers light, moderate multi-road, major shelter outage, capacity shortage, connectivity-breaking, high participation, localized hazard, and multi-area correlated disruption families.

Every row stores its scenario JSON, seed-derived ID, source hashes, exact state signatures, runtime, reference engine version, and `REFERENCE_SIMULATION_LABEL`. The generator resumes by scenario ID and never treats AI output as a label.
