# Goal 3A — Flood fidelity requirements

The simulator must label flood claims by evidence level:

| Level | Allowed claim | Minimum evidence | Current status |
| --- | --- | --- | --- |
| A | Relative scenario hazard / prioritization field | aligned high-resolution terrain plus rainfall time series; transparent assumptions; no depth or probability claim | Not yet runnable: raster and rainfall are blocked |
| B | Locally validated relative hazard | Level A plus Anyang flood traces/depth labels and held-out validation | Blocked: no local labels |
| C | Quantitative depth/time prediction | Level B plus authoritative drainage/inlet/sewer topology, hydraulic parameters, calibrated observations, uncertainty and held-out events | Drop for Goal 3B until inputs exist |

Synthetic SWMM or Shenzhen/UKEA benchmark outputs can validate software plumbing and tensor shapes only. They cannot be presented as Anyang flood truth. Every artifact therefore carries one of `SYNTHETIC`, `BENCHMARK`, `ANYANG_OFFICIAL`, or `FUTURE_ANYANG` provenance.

Required future Anyang inputs: DEM/DSM raster with CRS and vertical datum, rainfall gauges or radar time series, imperviousness/land-cover and roughness, stream/outfall boundaries, authoritative drainage/inlet/sewer network, observed flood extents or depths, and calibration/validation events.
