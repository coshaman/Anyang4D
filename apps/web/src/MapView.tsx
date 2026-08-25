import { useEffect, useRef } from "react";
import * as maplibregl from "maplibre-gl";
import type { Map as MapInstance, MapMouseEvent } from "maplibre-gl";
import type { Facility } from "./realData";

type Props = {
  facilities: Facility[];
  onSelect: (facility: Facility) => void;
  currentLocation: { latitude: number; longitude: number } | null;
  hazardGeometry?: Record<string, unknown> | null;
  hazardLabel?: string | null;
  onMapClick?: (point: { latitude: number; longitude: number }) => void;
  changedRoads?: Array<{ a: [number, number]; b: [number, number]; reason?: string }>;
  facilityLoads?: Record<string, number>;
};

export function MapView({ facilities, onSelect, currentLocation, hazardGeometry = null, hazardLabel = null, onMapClick, changedRoads = [], facilityLoads = {} }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const map = useRef<MapInstance | null>(null);
  const onSelectRef = useRef(onSelect);
  onSelectRef.current = onSelect;
  const onMapClickRef = useRef(onMapClick);
  onMapClickRef.current = onMapClick;

  const geojson = {
    type: "FeatureCollection" as const,
    features: facilities.filter((facility) => facility.latitude !== null && facility.longitude !== null).map((facility) => ({
      type: "Feature" as const,
      geometry: { type: "Point" as const, coordinates: [facility.longitude as number, facility.latitude as number] },
      properties: { id: facility.id, name: facility.name ?? "이름 미상", category: facility.category, load: facilityLoads[facility.id] ?? 0 }
    }))
  };

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
    instance.addControl(new maplibregl.NavigationControl({ showCompass: true }), "top-right");
    instance.addControl(new maplibregl.GeolocateControl({ positionOptions: { enableHighAccuracy: true }, trackUserLocation: false }), "top-right");
    instance.on("load", () => {
      instance.addSource("facilities", { type: "geojson", data: geojson, cluster: true, clusterMaxZoom: 14, clusterRadius: 44 });
      instance.addSource("scenario-hazard", { type: "geojson", data: hazardGeometry ? { type: "Feature", geometry: hazardToGeoJson(hazardGeometry), properties: { label: hazardLabel ?? "시나리오 영역" } } : emptyFeatureCollection });
      instance.addSource("scenario-closures", { type: "geojson", data: roadGeoJson(changedRoads) });
      instance.addLayer({ id: "scenario-hazard-fill", type: "fill", source: "scenario-hazard", paint: { "fill-color": "#c77a24", "fill-opacity": 0.22 } });
      instance.addLayer({ id: "scenario-hazard-line", type: "line", source: "scenario-hazard", paint: { "line-color": "#8b4f12", "line-width": 3, "line-dasharray": [2, 1] } });
      instance.addLayer({ id: "scenario-closures-line", type: "line", source: "scenario-closures", paint: { "line-color": "#9b2c2c", "line-width": 4, "line-dasharray": [1, 1] } });
      instance.addLayer({ id: "facility-clusters", type: "circle", source: "facilities", filter: ["has", "point_count"], paint: { "circle-color": "#0a6472", "circle-radius": ["step", ["get", "point_count"], 18, 50, 24, 100, 30], "circle-stroke-color": "#ffffff", "circle-stroke-width": 2 } });
      instance.addLayer({ id: "facility-cluster-count", type: "symbol", source: "facilities", filter: ["has", "point_count"], layout: { "text-field": "{point_count_abbreviated}", "text-size": 13 }, paint: { "text-color": "#ffffff" } });
      instance.addLayer({ id: "facility-points", type: "circle", source: "facilities", filter: ["!", ["has", "point_count"]], paint: { "circle-color": "#0a6472", "circle-radius": ["step", ["get", "load"], 7, 1, 9, 100, 11], "circle-stroke-color": "#ffffff", "circle-stroke-width": 2 } });
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
      instance.on("click", (event: MapMouseEvent) => onMapClickRef.current?.({ latitude: event.lngLat.lat, longitude: event.lngLat.lng }));
    });
    return () => { instance.remove(); map.current = null; };
    // The source data is updated in the effect below.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
    if (currentLocation && map.current) {
      map.current.easeTo({ center: [currentLocation.longitude, currentLocation.latitude], zoom: 15 });
    }
  }, [currentLocation]);

  return <div className="map-wrap"><div ref={container} className="real-map" aria-label="안양 실제 지도" /><p className="map-attribution">© OpenStreetMap contributors · 지도 타일 제공 약관을 확인하세요.</p></div>;
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
