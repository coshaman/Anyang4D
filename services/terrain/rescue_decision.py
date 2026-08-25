from __future__ import annotations


def decide_rescue(classes: dict[str, str]) -> dict[str, object]:
    rank = {"TERRAIN_C": 0, "TERRAIN_B": 1, "TERRAIN_A": 2}
    valid = [name for name, value in classes.items() if value in rank]
    final_class = max((classes[name] for name in valid), key=lambda value: rank[value], default="TERRAIN_C")
    passes_b = rank[final_class] >= rank["TERRAIN_B"]
    passes_a = final_class == "TERRAIN_A"
    return {
        "final_terrain_class": final_class,
        "LEVEL_A_FLOOD_NEXT_GOAL_AUTHORIZED": passes_a,
        "ADMIN_LEVEL_A_FLOOD_ELIGIBLE": passes_b,
        "CITIZEN_ROAD_HAZARD_FUTURE_ELIGIBILITY": False,
        "STREET_LEVEL_FLOOD_TERRAIN_PATH": "KEEP" if passes_b else "DROP",
        "CITIZEN_HAZARD_ROUTING_FROM_TERRAIN": "KEEP" if passes_b else "DROP",
    }

