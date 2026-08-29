# SAFE-Twin Anyang V2 Product Realignment Design

## Goal

Restore SAFE-Twin Anyang as one map-centered product with three user modes: 시민, 행사 안내, and 재난 시뮬레이션/고급 분석. Remove unsupported scientific claims and make the remaining 2.5D, 4D, routing, event-plan, public-page, and deterministic-video workflows demonstrable in the browser.

## Product boundaries

The product will not expose or promise SOLWEIG/Tmrt/UTCI, PhysicsNeMo/FNO microclimate, Cool AI route, authoritative solar shadows, physical-terrain flood prediction/depth, rain-aware flood routing, or land-cover-dependent Nature route. Old artifacts remain research history only and are not shown as pending features.

The exact existing scenario backend remains the source of truth for administrative what-if results. Event routes are always labeled as organizer-designated guidance and are never certified as legal or fire-code compliant.

## Architecture

`MapView` becomes the shared visual core. It owns a single MapLibre map instance, 2D/3D camera state, building fill-extrusion, facility markers, route layers, scenario hazard/closure layers, and aggregated evacuation-flow layers. Its data inputs remain plain GeoJSON and typed props so citizen, event, and admin modes share the same map.

Event authoring is a browser-first workflow. An `EventPlan` contains event metadata, venue representation, image-local floor-plan data when supplied, groups, nodes, and manually approved route polylines. Outdoor plans may use the existing OSM route service; indoor routes are drawn by the organizer and never inferred. A URL-safe encoded plan token is used for share links and QR generation; large image uploads remain local to the authoring browser and are offered as plan export/import when they cannot fit in a URL.

The public event route is `/event/{slug}`. The SPA decodes `?plan=` first and falls back to a deterministic built-in demo plan. QR is generated without a dependency using a small vendored/stdlib-compatible encoder already available in the repository if present; otherwise the first release uses a QR-ready URL plus a canvas/SVG matrix implementation covered by tests. No paid API or external persistence dependency is introduced.

Evacuation video is deterministic SVG/canvas composition driven by the same `EventPlan`. Six storyboard scenes are rendered into a 1920×1080 logical canvas: title, start area, exit, route to exit, route to assembly, and organizer instructions. `MediaRecorder` exports WebM from `canvas.captureStream()`. Preview, play/pause, restart, fullscreen, reduced-motion static mode, and nonempty export are required; browser TTS is optional and never part of authoritative export.

## Mode and UI structure

The normal citizen screen contains search, map/current location, selected destination/route, nearby facilities, and a concise training/event link. It does not expose solver names, edge IDs, provenance enums, AI screening, capacity overrides, or diagnostics. `/admin` is split into `행사 안내`, `재난 시뮬레이션`, and `고급 분석`; advanced controls are hidden behind the latter workspace.

The event workspace provides a short stepper: event details, outdoor/indoor venue, points and groups, route drawing, preview, and share/video. The floor-plan canvas stores image-local coordinates. The public page shows event name, map/floor plan, current group/location, exit, assembly point, emergency actions, optional AED/contact, and video, with one concise organizer verification notice.

## Data contracts

Building properties are normalized as `{height_m: number | null, height_provenance: "OSM_HEIGHT" | "DERIVED_LEVEL_HEIGHT" | "UNKNOWN_HEIGHT"}`. Priority is OSM `height`, then `building:levels * 3.0`, otherwise flat/visual-only. Approximate values are never labeled official.

An `EventPlan` uses:

```ts
type EventPlan = {
  slug: string; name: string; venue: string;
  representation: "OUTDOOR" | "INDOOR";
  floorPlan?: { mimeType: "image/png" | "image/jpeg" | "image/svg+xml" | "application/pdf"; dataUrl: string; width: number; height: number };
  groups: Array<{ id: string; name: string; start: Point; exit: Point; assembly: Point; route: Point[]; color: string }>;
  optionalFacilities: Array<{ kind: "AED" | "EXTINGUISHER" | "STAIRS" | "RESTRICTED_ZONE"; point: Point; label?: string }>;
  emergencyInstructions: string[]; organizerContact?: string; logoDataUrl?: string;
};
type Point = { x: number; y: number };
```

For outdoor map coordinates, `Point` is replaced by `{latitude, longitude}` in a route-specific wrapper; indoor points are always image-local. All public displays use the organizer-designated wording.

## Verification gates

Each phase adds behavior-first tests before implementation: building source/layer and camera controls; scenario source differences at four times; route geometry/origin/destination/fit bounds and two candidates where available; event node/route editing; public URL and QR resolution; storyboard scene advancement and WebM byte output; citizen jargon absence. Playwright screenshots are captured at 390×844, 768×1024, 1280×720, and 1440×900 for the required screens, then visually inspected.

## Known limitations

URL tokens cannot safely carry arbitrary large binary floor plans. The authoring UI will provide JSON export/import and mark large assets as local-only unless the user shares the exported asset with the plan. The browser determines WebM codec support; unsupported export is a visible error, not a fake download.
