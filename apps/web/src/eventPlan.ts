export type EventPoint = { x: number; y: number };
export type OutdoorPoint = { latitude: number; longitude: number };
export type EventRepresentation = "OUTDOOR" | "INDOOR";
export type OptionalFacilityKind = "AED" | "EXTINGUISHER" | "STAIRS" | "RESTRICTED_ZONE";
export type EventGroup = { id: string; name: string; start: EventPoint | null; exit: EventPoint | null; assembly: EventPoint | null; route: EventPoint[]; outdoorStart: OutdoorPoint | null; outdoorExit: OutdoorPoint | null; outdoorAssembly: OutdoorPoint | null; outdoorRoute: OutdoorPoint[]; routeLabel: string; color: string };
export type EventVideoConfig = { title: string; sceneDurationSeconds: number; textSize: "standard" | "large" | "compact"; narration: "caption" | "tts-preview"; logoDataUrl?: string };
export type EventPlan = {
  version: 1;
  slug: string;
  name: string;
  venue: string;
  representation: EventRepresentation;
  floorPlan?: { mimeType: "image/png" | "image/jpeg" | "image/svg+xml" | "application/pdf"; dataUrl: string; width: number; height: number };
  groups: EventGroup[];
  optionalFacilities: Array<{ kind: OptionalFacilityKind; point: EventPoint; label?: string }>;
  emergencyInstructions: string[];
  organizerContact?: string;
  logoDataUrl?: string;
  videoConfig?: EventVideoConfig;
};

const groupColors = ["#0a6472", "#b34a3c", "#9a6300"];

export function createEventPlan(name: string, venue: string, representation: EventRepresentation): EventPlan {
  return {
    version: 1,
    slug: slugify(name),
    name,
    venue,
    representation,
    groups: ["A", "B", "C"].map((id, index) => ({ id, name: `${id}구역`, start: null, exit: null, assembly: null, route: [], outdoorStart: null, outdoorExit: null, outdoorAssembly: null, outdoorRoute: [], routeLabel: "", color: groupColors[index] })),
    optionalFacilities: [],
    emergencyInstructions: ["뛰지 마세요", "안내요원의 지시에 따르세요", "위급 시 119에 신고하세요"],
    videoConfig: { title: "", sceneDurationSeconds: 3, textSize: "standard", narration: "caption" },
  };
}

export function addEventNode(plan: EventPlan, groupId: string, kind: "start" | "exit" | "assembly" | "AED" | "EXTINGUISHER" | "STAIRS" | "RESTRICTED_ZONE", point: EventPoint): EventPlan {
  if (["start", "exit", "assembly"].includes(kind)) {
    return updateEventGroup(plan, groupId, { [kind]: point } as Partial<EventGroup>);
  }
  return { ...plan, optionalFacilities: [...plan.optionalFacilities, { kind: kind as OptionalFacilityKind, point }] };
}

export function updateEventGroup(plan: EventPlan, groupId: string, update: Partial<EventGroup>): EventPlan {
  return { ...plan, groups: plan.groups.map((group) => group.id === groupId ? { ...group, ...update } : group) };
}

export function addRoutePoint(plan: EventPlan, groupId: string, point: EventPoint): EventPlan {
  return updateEventGroup(plan, groupId, { route: [...(plan.groups.find((group) => group.id === groupId)?.route ?? []), point] });
}

export function removeLastRoutePoint(plan: EventPlan, groupId: string): EventPlan {
  const route = plan.groups.find((group) => group.id === groupId)?.route ?? [];
  return updateEventGroup(plan, groupId, { route: route.slice(0, -1) });
}

export function addOutdoorNode(plan: EventPlan, groupId: string, kind: "start" | "exit" | "assembly", point: OutdoorPoint): EventPlan {
  const field = `outdoor${kind[0].toUpperCase()}${kind.slice(1)}` as "outdoorStart" | "outdoorExit" | "outdoorAssembly";
  return updateEventGroup(plan, groupId, { [field]: point } as Partial<EventGroup>);
}

export function addOutdoorRoutePoint(plan: EventPlan, groupId: string, point: OutdoorPoint): EventPlan {
  return updateEventGroup(plan, groupId, { outdoorRoute: [...(plan.groups.find((group) => group.id === groupId)?.outdoorRoute ?? []), point] });
}

export function clearEventNode(plan: EventPlan, groupId: string, kind: "start" | "exit" | "assembly"): EventPlan {
  return updateEventGroup(plan, groupId, { [kind]: null, [`outdoor${kind[0].toUpperCase()}${kind.slice(1)}`]: null } as Partial<EventGroup>);
}

export function removeLastOutdoorRoutePoint(plan: EventPlan, groupId: string): EventPlan {
  const route = plan.groups.find((group) => group.id === groupId)?.outdoorRoute ?? [];
  return updateEventGroup(plan, groupId, { outdoorRoute: route.slice(0, -1) });
}

export function encodeEventPlan(plan: EventPlan): string {
  const bytes = new TextEncoder().encode(JSON.stringify(plan));
  let binary = "";
  bytes.forEach((byte) => { binary += String.fromCharCode(byte); });
  return btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/, "");
}

export function decodeEventPlan(token: string): EventPlan {
  const binary = atob(token.replaceAll("-", "+").replaceAll("_", "/") + "=".repeat((4 - token.length % 4) % 4));
  return JSON.parse(new TextDecoder().decode(Uint8Array.from(binary, (char) => char.charCodeAt(0))) as string) as EventPlan;
}

export function buildEventShareUrl(plan: EventPlan, origin = window.location.origin) {
  return `${origin.replace(/\/$/, "")}/event/${encodeURIComponent(plan.slug || "event")}?plan=${encodeURIComponent(encodeEventPlan(plan))}`;
}

function slugify(value: string) {
  return value.trim().toLowerCase().replace(/[^\p{Letter}\p{Number}]+/gu, "-").replace(/^-|-$/g, "") || "event";
}
