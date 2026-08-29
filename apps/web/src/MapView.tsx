import { useEffect, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";
import maplibreWorkerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";
import type { FillExtrusionLayerSpecification, Map as MapInstance, MapMouseEvent } from "maplibre-gl";
import type { Facility } from "./realData";
import { osmBuildings, type OSMBuilding } from "./buildings";

maplibregl.setWorkerUrl(maplibreWorkerUrl);

type Props = {
  facilities: Facility[];
  onSelect: (facility: Facility) => void;
  currentLocation: { latitude: number; longitude: number } | null;
  hazardGeometry?: Record<string, unknown> | null;
  hazardLabel?: string | null;
  onMapClick?: (point: { latitude: number; longitude: number }) => void;
  changedRoads?: Array<{ a: [number, number]; b: [number, number]; reason?: string }>;
  facilityLoads?: Record<string, number>;
  walkingRoute?: { geometry: Array<{ latitude: number; longitude: number }>; origin: { latitude: number; longitude: number }; destination: { latitude: number; longitude: number } } | null;
  buildings?: Building[];
  evacuationFlow?: EvacuationFlow[];
  facilityLoadRatios?: Record<string, number>;
  eventSafetyPoints?: Array<{ kind: string; point: { latitude: number; longitude: number }; label?: string }>;
};

export type EvacuationFlow = {
  demand_node_id: string;
  shelter_id: string;
  assigned_demand: number;
  load_ratio: number;
  geometry: { type: "LineString"; coordinates: number[][] };
};

export type Building = {
  id: string;
  geometry: { type: "Polygon"; coordinates: number[][][] };
  height_m: number;
  height_provenance: "OSM_HEIGHT" | "DERIVED_LEVEL_HEIGHT" | "UNKNOWN_HEIGHT";
};

export function normalizeBuilding(building: OSMBuilding): Building {
  const height = Number.parseFloat(building.tags.height ?? "");
  if (Number.isFinite(height) && height > 0) return { id: building.id, geometry: building.geometry, height_m: height, height_provenance: "OSM_HEIGHT" };
  const levels = Number.parseFloat(building.tags["building:levels"] ?? "");
  if (Number.isFinite(levels) && levels > 0) return { id: building.id, geometry: building.geometry, height_m: levels * 3, height_provenance: "DERIVED_LEVEL_HEIGHT" };
  return { id: building.id, geometry: building.geometry, height_m: 0, height_provenance: "UNKNOWN_HEIGHT" };
}

export function buildBuildingGeoJson(buildings: Building[]) {
  return { type: "FeatureCollection" as const, features: buildings.map((building) => ({ type: "Feature" as const, geometry: building.geometry, properties: { id: building.id, height_m: building.height_m, height_provenance: building.height_provenance } })) };
}

export function buildBuildingExtrusionLayer() {
  return { id: "building-extrusion", type: "fill-extrusion" as const, source: "buildings", minzoom: 10, paint: { "fill-extrusion-color": "#679b9a", "fill-extrusion-height": ["get", "height_m"], "fill-extrusion-base": 0, "fill-extrusion-opacity": 0.72 } } as FillExtrusionLayerSpecification;
}

export function buildEvacuationFlowGeoJson(flows: EvacuationFlow[]) {
  return { type: "FeatureCollection" as const, features: flows.map((flow) => ({ type: "Feature" as const, geometry: flow.geometry, properties: { demand_node_id: flow.demand_node_id, shelter_id: flow.shelter_id, assigned_demand: flow.assigned_demand, load_ratio: flow.load_ratio } })) };
}

export function MapView({ facilities, onSelect, currentLocation, hazardGeometry = null, hazardLabel = null, onMapClick, changedRoads = [], facilityLoads = {}, walkingRoute = null, buildings = osmBuildings.map(normalizeBuilding), evacuationFlow = [], facilityLoadRatios = {}, eventSafetyPoints = [] }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const map = useRef<MapInstance | null>(null);
  const onSelectRef = useRef(onSelect);
  onSelectRef.current = onSelect;
  const onMapClickRef = useRef(onMapClick);
  onMapClickRef.current = onMapClick;
  const dynamicProps = useRef({ geojson: null as typeof geojson | null, hazardGeometry, hazardLabel, changedRoads, walkingRoute, eventSafetyPoints });
  const [viewMode, setViewMode] = useState<"2D" | "3D">("2D");

  const geojson = {
    type: "FeatureCollection" as const,
    features: facilities.filter((facility) => facility.latitude !== null && facility.longitude !== null).map((facility) => ({
      type: "Feature" as const,
      geometry: { type: "Point" as const, coordinates: [facility.longitude as number, facility.latitude as number] },
      properties: { id: facility.id, name: facility.name ?? "이름 미상", category: facility.category, load: facilityLoads[facility.id] ?? 0, load_ratio: facilityLoadRatios[facility.id] ?? evacuationFlow.find((flow) => flow.shelter_id === facility.id)?.load_ratio ?? 0 }
    }))
  };
  dynamicProps.current = { geojson, hazardGeometry, hazardLabel, changedRoads, walkingRoute, eventSafetyPoints };

  useEffect(() => {
    if (!container.current || map.current || typeof window === "undefined" || !(window as Window & { WebGLRenderingContext?: unknown }).WebGLRenderingContext || !maplibregl?.Map) return;
    const instance = new maplibregl.Map({
      container: container.current,
      center: [126.95, 37.4],
      zoom: 12.4,
      minZoom: 10,
      maxZoom: 18,
      style: {
        version: 8,
        sources: navigator.webdriver ? {} : {
          osm: { type: "raster", tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"], tileSize: 256, attribution: "© OpenStreetMap contributors" }
        },
        layers: navigator.webdriver ? [] : [{ id: "osm", type: "raster", source: "osm" }]
      }
    });
    map.current = instance;
    (window as Window & { __SAFE_TWIN_MAP__?: MapInstance }).__SAFE_TWIN_MAP__ = instance;
    instance.addControl(new maplibregl.NavigationControl({ showCompass: true }), "top-right");
    instance.addControl(new maplibregl.GeolocateControl({ positionOptions: { enableHighAccuracy: true }, trackUserLocation: false }), "top-right");
    instance.on("load", () => {
      const current = dynamicProps.current;
      instance.addSource("facilities", { type: "geojson", data: current.geojson ?? geojson, cluster: true, clusterMaxZoom: 14, clusterRadius: 44 });
      instance.addSource("scenario-hazard", { type: "geojson", data: current.hazardGeometry ? { type: "Feature", geometry: hazardToGeoJson(current.hazardGeometry), properties: { label: current.hazardLabel ?? "시나리오 영역" } } : emptyFeatureCollection });
      instance.addSource("scenario-closures", { type: "geojson", data: roadGeoJson(current.changedRoads) });
      instance.addSource("walking-route", { type: "geojson", data: routeGeoJson(current.walkingRoute) });
      instance.addSource("event-safety-points", { type: "geojson", data: eventSafetyPointGeoJson(current.eventSafetyPoints) });
      instance.addSource("buildings", { type: "geojson", data: buildBuildingGeoJson(buildings) });
      instance.addSource("evacuation-flow", { type: "geojson", data: buildEvacuationFlowGeoJson(evacuationFlow) });
      instance.addLayer({ id: "scenario-hazard-fill", type: "fill", source: "scenario-hazard", paint: { "fill-color": "#c77a24", "fill-opacity": 0.22 } });
      instance.addLayer({ id: "scenario-hazard-line", type: "line", source: "scenario-hazard", paint: { "line-color": "#8b4f12", "line-width": 3, "line-dasharray": [2, 1] } });
      instance.addLayer({ id: "scenario-closures-line", type: "line", source: "scenario-closures", paint: { "line-color": "#9b2c2c", "line-width": 4, "line-dasharray": [1, 1] } });
      instance.addLayer({ id: "walking-route-line", type: "line", source: "walking-route", filter: ["==", ["geometry-type"], "LineString"], paint: { "line-color": "#1457a6", "line-width": 5, "line-opacity": 0.9 } });
      instance.addLayer({ id: "walking-route-points", type: "circle", source: "walking-route", filter: ["==", ["geometry-type"], "Point"], paint: { "circle-color": ["match", ["get", "role"], "origin", "#16805b", "#b34a3c"], "circle-radius": 8, "circle-stroke-color": "#ffffff", "circle-stroke-width": 2 } });
      instance.addLayer({ id: "event-safety-points", type: "circle", source: "event-safety-points", paint: { "circle-color": ["match", ["get", "kind"], "AED", "#16805b", "RESTRICTED_ZONE", "#9b2c2c", "#b8751b"], "circle-radius": 9, "circle-stroke-color": "#ffffff", "circle-stroke-width": 2 } });
      instance.addLayer({ id: "event-safety-labels", type: "symbol", source: "event-safety-points", layout: { "text-field": ["get", "label"], "text-size": 12, "text-offset": [0, 1.25], "text-anchor": "top" }, paint: { "text-color": "#173d43", "text-halo-color": "#ffffff", "text-halo-width": 1.5 } });
      instance.addLayer({ id: "building-footprints", type: "fill", source: "buildings", paint: { "fill-color": "#8ab8b2", "fill-opacity": 0.26 } });
      instance.addLayer(buildBuildingExtrusionLayer());
      instance.addLayer({ id: "evacuation-flow-lines", type: "line", source: "evacuation-flow", paint: { "line-color": "#d26a2e", "line-opacity": 0.78, "line-width": ["interpolate", ["linear"], ["get", "assigned_demand"], 1, 1.5, 100, 3, 1000, 8] } });
      instance.addLayer({ id: "facility-clusters", type: "circle", source: "facilities", filter: ["has", "point_count"], paint: { "circle-color": "#0a6472", "circle-radius": ["step", ["get", "point_count"], 18, 50, 24, 100, 30], "circle-stroke-color": "#ffffff", "circle-stroke-width": 2 } });
      instance.addLayer({ id: "facility-cluster-count", type: "symbol", source: "facilities", filter: ["has", "point_count"], layout: { "text-field": "{point_count_abbreviated}", "text-size": 13 }, paint: { "text-color": "#ffffff" } });
      instance.addLayer({ id: "facility-points", type: "circle", source: "facilities", filter: ["!", ["has", "point_count"]], paint: { "circle-color": "#0a6472", "circle-radius": ["interpolate", ["linear"], ["get", "load_ratio"], 0, 7, 0.5, 10, 1, 14, 1.5, 18], "circle-stroke-color": "#ffffff", "circle-stroke-width": 2 } });
      if (current.walkingRoute && current.walkingRoute.geometry.length > 1) {
        const bounds = new maplibregl.LngLatBounds();
        current.walkingRoute.geometry.forEach((point) => bounds.extend([point.longitude, point.latitude]));
        instance.fitBounds(bounds, { padding: 64, maxZoom: 16, duration: 0 });
      }
      instance.on("click", "facility-clusters", (event: MapMouseEvent) => {
        const feature = instance.queryRenderedFeatures(event.point, { layers: ["facility-clusters"] })[0];
        const clusterId = feature?.properties?.cluster_id;
        if (clusterId === undefined) return;
        (instance.getSource("facilities") as maplibregl.GeoJSONSource).getClusterExpansionZoom(clusterId).then((zoom: number) => {
          instance.easeTo({ center: (feature.geometry as { coordinates: [number, number] }).coordinates, zoom });
        });
      });
      instance.on("click", "facility-points", (event: MapMouseEvent) => {
        const feature = instance.queryRenderedFeatures(event.point, { layers: ["facility-points"] })[0];
        const id = feature?.properties?.id;
        const facility = facilities.find((candidate) => candidate.id === id);
        if (facility) onSelectRef.current(facility);
      });
      instance.on("mouseenter", "facility-points", () => { instance.getCanvas().style.cursor = "pointer"; });
      instance.on("mouseleave", "facility-points", () => { instance.getCanvas().style.cursor = ""; });
      instance.on("click", (event: MapMouseEvent) => {
        const clickedFacility = instance.queryRenderedFeatures(event.point, { layers: ["facility-points"] }).length > 0;
        if (!clickedFacility) onMapClickRef.current?.({ latitude: event.lngLat.lat, longitude: event.lngLat.lng });
      });
    });
    return () => { instance.remove(); map.current = null; const debugWindow = window as Window & { __SAFE_TWIN_MAP__?: MapInstance }; if (debugWindow.__SAFE_TWIN_MAP__ === instance) delete debugWindow.__SAFE_TWIN_MAP__; };
    // The source data is updated in the effect below.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const source = map.current?.getSource("buildings") as maplibregl.GeoJSONSource | undefined;
    source?.setData(buildBuildingGeoJson(buildings));
  }, [buildings]);

  useEffect(() => {
    const source = map.current?.getSource("evacuation-flow") as maplibregl.GeoJSONSource | undefined;
    source?.setData(buildEvacuationFlowGeoJson(evacuationFlow));
  }, [evacuationFlow]);

  useEffect(() => {
    const instance = map.current;
    if (!instance) return;
    if (instance.getLayer("building-footprints")) instance.setLayoutProperty("building-footprints", "visibility", viewMode === "2D" ? "visible" : "none");
    if (instance.getLayer("building-extrusion")) instance.setLayoutProperty("building-extrusion", "visibility", viewMode === "3D" ? "visible" : "none");
    instance.easeTo({ pitch: viewMode === "3D" ? 52 : 0, duration: 500 });
  }, [viewMode]);

  useEffect(() => {
    const source = map.current?.getSource("facilities") as maplibregl.GeoJSONSource | undefined;
    source?.setData(geojson);
  }, [facilities, facilityLoads]);

  useEffect(() => {
    const source = map.current?.getSource("scenario-closures") as maplibregl.GeoJSONSource | undefined;
    source?.setData(roadGeoJson(changedRoads));
  }, [changedRoads]);

  useEffect(() => {
    const source = map.current?.getSource("scenario-hazard") as maplibregl.GeoJSONSource | undefined;
    source?.setData(hazardGeometry ? { type: "Feature", geometry: hazardToGeoJson(hazardGeometry), properties: { label: hazardLabel ?? "시나리오 영역" } } : emptyFeatureCollection);
  }, [hazardGeometry, hazardLabel]);

  useEffect(() => {
    const source = map.current?.getSource("walking-route") as maplibregl.GeoJSONSource | undefined;
    source?.setData(routeGeoJson(walkingRoute));
    if (walkingRoute && map.current && walkingRoute.geometry.length > 1) {
      const bounds = new maplibregl.LngLatBounds();
      walkingRoute.geometry.forEach((point) => bounds.extend([point.longitude, point.latitude]));
      map.current.fitBounds(bounds, { padding: 64, maxZoom: 16, duration: 400 });
    }
  }, [walkingRoute]);

  useEffect(() => {
    const source = map.current?.getSource("event-safety-points") as maplibregl.GeoJSONSource | undefined;
    source?.setData(eventSafetyPointGeoJson(eventSafetyPoints));
  }, [eventSafetyPoints]);

  useEffect(() => {
    if (currentLocation && map.current) {
      map.current.easeTo({ center: [currentLocation.longitude, currentLocation.latitude], zoom: 15 });
    }
  }, [currentLocation]);

  return <div className="map-wrap"><div className="map-camera-controls" aria-label="지도 보기 조작"><button type="button" data-testid="map-2d-toggle" aria-pressed={viewMode === "2D"} onClick={() => setViewMode("2D")}>2D</button><button type="button" data-testid="map-3d-toggle" aria-pressed={viewMode === "3D"} onClick={() => setViewMode("3D")}>3D</button><button type="button" onClick={() => map.current?.easeTo({ pitch: Math.min(75, (map.current.getPitch?.() ?? 0) + 12), duration: 350 })}>기울이기</button><button type="button" onClick={() => map.current?.rotateTo((map.current.getBearing?.() ?? 0) + 30, { duration: 350 })}>회전</button><button type="button" onClick={() => map.current?.easeTo({ bearing: 0, pitch: viewMode === "3D" ? 52 : 0, duration: 400 })}>북쪽</button></div><div ref={container} className="real-map" aria-label={`안양 실제 지도 ${viewMode} 보기`} />{viewMode === "3D" && <p className="map-3d-note" role="status">3D 건물 높이 · OSM 태그 우선 · 미상 높이는 평면 표시</p>}{evacuationFlow.length > 0 && <p className="map-flow-legend" role="status">대피 수요 이동 · 선 굵기 = 배정 수요</p>}{walkingRoute && <p className="map-route-legend" data-testid="walking-route-line" aria-label="기본 도보 경로 지도 레이어">파란 선: 기본 도보 네트워크 경로 · 재난 안전경로 아님</p>}<p className="map-attribution">© OpenStreetMap contributors · 지도 타일 제공 약관을 확인하세요.</p></div>;
}

const emptyFeatureCollection = { type: "FeatureCollection" as const, features: [] };

function hazardToGeoJson(hazard: Record<string, unknown>) {
  if (hazard.kind === "polygon") return { type: "Polygon" as const, coordinates: hazard.coordinates as number[][][] };
  if (hazard.kind === "multipolygon") return { type: "MultiPolygon" as const, coordinates: hazard.coordinates as number[][][][] };
  if (hazard.kind === "point_radius") return { type: "Point" as const, coordinates: hazard.center as number[] };
  if (hazard.kind === "corridor") return { type: "LineString" as const, coordinates: hazard.coordinates as number[][] };
  return { type: "GeometryCollection" as const, geometries: [] };
}

function roadGeoJson(roads: Array<{ a: [number, number]; b: [number, number]; reason?: string }>) {
  return { type: "FeatureCollection" as const, features: roads.map((road) => ({ type: "Feature" as const, geometry: { type: "LineString" as const, coordinates: [road.a, road.b] }, properties: { reason: road.reason ?? "시나리오에서 통행 제한으로 설정된 도로" } })) };
}

function routeGeoJson(route: Props["walkingRoute"]) {
  if (!route) return emptyFeatureCollection;
  return { type: "FeatureCollection" as const, features: [
    { type: "Feature" as const, geometry: { type: "LineString" as const, coordinates: route.geometry.map((point) => [point.longitude, point.latitude]) }, properties: { role: "route" } },
    { type: "Feature" as const, geometry: { type: "Point" as const, coordinates: [route.origin.longitude, route.origin.latitude] }, properties: { role: "origin" } },
    { type: "Feature" as const, geometry: { type: "Point" as const, coordinates: [route.destination.longitude, route.destination.latitude] }, properties: { role: "destination" } },
  ] };
}

export function eventSafetyPointGeoJson(points: NonNullable<Props["eventSafetyPoints"]>) {
  const labels: Record<string, string> = { AED: "AED", EXTINGUISHER: "소화기", STAIRS: "계단", RESTRICTED_ZONE: "출입 제한" };
  return { type: "FeatureCollection" as const, features: points.map((item) => ({ type: "Feature" as const, geometry: { type: "Point" as const, coordinates: [item.point.longitude, item.point.latitude] }, properties: { kind: item.kind, label: item.label || labels[item.kind] || item.kind } })) };
}
