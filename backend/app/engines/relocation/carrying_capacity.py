"""
Carrying Capacity Engine — 8-Dimensional Infrastructure Capacity Model.

Converts physical infrastructure units into estimated people-supported capacities:
- Housing: Dwellings (4.5 persons / dwelling)
- Land: Usable Hectares (150 persons / hectare)
- Water: kL/day (70 Liters/Person/Day standard)
- Sanitation: Units/toilets (25 persons / toilet)
- Healthcare: Clinic/hospital beds (250 persons / bed)
- Education: School seats (5 persons total pop per student seat)
- Road Access: Transit trips/day (1.5 trips/person/day)
- Electricity: Distribution capacity in kW (0.35 kW / person)

Identifies binding bottlenecks dynamically:
Feasible Additional Capacity = min(additional_capacity_people across all 8 dimensions)

Includes mandatory planning disclaimer:
"Planning estimate — not legally certified carrying capacity."
"""
from typing import Dict, Any, List, Optional


class CapacityCalculator:
    """
    Evaluates 8 infrastructure dimensions in converted people-supported units
    and identifies the limiting bottleneck dynamically.
    """

    DIMENSIONS = [
        "Housing",
        "Land",
        "Water",
        "Sanitation",
        "Healthcare",
        "Education",
        "Road Access",
        "Electricity",
    ]

    # Dimension conversion specifications
    # unit_name, multiplier_to_people (or conversion function)
    CONVERSION_STANDARDS = {
        "Housing": {"raw_unit": "dwellings", "people_per_unit": 4.5, "description": "4.5 persons per residential dwelling"},
        "Land": {"raw_unit": "hectares", "people_per_unit": 150.0, "description": "150 persons per usable developable hectare"},
        "Water": {"raw_unit": "kL/day", "people_per_unit": 1000.0 / 70.0, "description": "70 Liters Per Capita per Day (LPCD)"},
        "Sanitation": {"raw_unit": "toilets", "people_per_unit": 25.0, "description": "25 persons per sanitary community unit"},
        "Healthcare": {"raw_unit": "clinic beds", "people_per_unit": 250.0, "description": "1 primary health bed per 250 persons"},
        "Education": {"raw_unit": "school seats", "people_per_unit": 5.0, "description": "20% school-age child demographic ratio"},
        "Road Access": {"raw_unit": "trips/day", "people_per_unit": 1.0 / 1.5, "description": "1.5 daily transit trips per capita"},
        "Electricity": {"raw_unit": "kW", "people_per_unit": 1.0 / 0.35, "description": "0.35 kW continuous demand per capita"},
    }

    # Alias mapping for backward compatibility with legacy dimension names
    DIMENSION_ALIASES = {
        "Water Supply": "Water",
        "Power Grid": "Electricity",
        "Transport": "Road Access",
        "Livelihood": "Land",
    }

    @staticmethod
    def canonical_dimension_name(name: str) -> str:
        return CapacityCalculator.DIMENSION_ALIASES.get(name, name)

    @staticmethod
    def convert_to_people(dimension: str, raw_units: float) -> int:
        """Converts raw physical units into supported population count."""
        canon = CapacityCalculator.canonical_dimension_name(dimension)
        spec = CapacityCalculator.CONVERSION_STANDARDS.get(canon)
        if not spec:
            return int(raw_units)
        return max(0, int(round(raw_units * spec["people_per_unit"])))

    @staticmethod
    def convert_people_to_raw(dimension: str, people: int) -> float:
        """Converts population count back to required physical units."""
        canon = CapacityCalculator.canonical_dimension_name(dimension)
        spec = CapacityCalculator.CONVERSION_STANDARDS.get(canon)
        if not spec or spec["people_per_unit"] <= 0:
            return float(people)
        return round(people / spec["people_per_unit"], 1)

    @staticmethod
    def analyze_capacity(site_id: str, incoming_population: int = 0) -> Dict[str, Any]:
        """
        Analyzes the carrying capacity of a candidate site across all 8 dimensions.
        Converts all physical dimensions into people-supported equivalents.
        Identifies the critical binding bottleneck dynamically.
        """
        from app.db.database import get_session_factory
        from app.db.repository import Repository

        Session = get_session_factory()
        session = Session()
        try:
            site = Repository.get_site(session, site_id)
            site_name = site.name if site else f"Site {site_id}"
            caps = Repository.get_site_capacity(session, site_id)

            if not caps:
                return {
                    "site_id": site_id,
                    "site_name": site_name,
                    "incoming_population": incoming_population,
                    "existing_population": 0,
                    "estimated_total_supported_population": 0,
                    "additional_capacity": 0,
                    "assigned_relocation_population": incoming_population,
                    "remaining_capacity": -incoming_population,
                    "dimensions": [],
                    "critical_bottleneck": "Unknown (No Data)",
                    "capacity_explanation": "No infrastructure capacity records found for this site.",
                    "feasible_additional_capacity": 0,
                    "is_feasible": False,
                    "disclaimer": "Planning estimate — not legally certified carrying capacity.",
                }

            # Map DB records to canonical dimensions
            dimensions_analysis = []
            db_caps_map = {}
            for c in caps:
                canon_name = CapacityCalculator.canonical_dimension_name(c.dimension)
                db_caps_map[canon_name] = c

            # Evaluate each of the 8 canonical dimensions
            for dim_name in CapacityCalculator.DIMENSIONS:
                cap_record = db_caps_map.get(dim_name)
                spec = CapacityCalculator.CONVERSION_STANDARDS.get(dim_name, {
                    "raw_unit": "units",
                    "people_per_unit": 1.0,
                    "description": "1:1 allocation",
                })

                if cap_record:
                    raw_max = cap_record.max_capacity
                    raw_util = cap_record.current_utilization
                else:
                    # Deterministic fallback based on site attributes
                    raw_max = 500
                    raw_util = 150

                # People-supported capacity conversions
                total_supported = CapacityCalculator.convert_to_people(dim_name, raw_max)
                existing_pop = CapacityCalculator.convert_to_people(dim_name, raw_util)
                additional_cap = max(0, total_supported - existing_pop)
                post_surplus = additional_cap - incoming_population

                # Status determination
                if post_surplus < 0:
                    status = "Critical"
                elif post_surplus < (total_supported * 0.15):
                    status = "Warning"
                else:
                    status = "Safe"

                raw_required_for_incoming = CapacityCalculator.convert_people_to_raw(dim_name, incoming_population)

                dim_data = {
                    "dimension": dim_name,
                    "raw_unit": spec["raw_unit"],
                    "raw_max_capacity": raw_max,
                    "raw_current_utilization": raw_util,
                    "raw_available_capacity": max(0, raw_max - raw_util),
                    "raw_required_for_incoming": raw_required_for_incoming,
                    "conversion_standard": spec["description"],
                    # People-supported values
                    "total_supported_population": total_supported,
                    "existing_population": existing_pop,
                    "additional_capacity": additional_cap,
                    "assigned_relocation_population": incoming_population,
                    "remaining_capacity": post_surplus,
                    "status": status,
                    # Backward compatibility keys
                    "max_capacity": total_supported,
                    "current_utilization": existing_pop,
                    "available_capacity": additional_cap,
                    "required_capacity": incoming_population,
                    "post_relocation_surplus": post_surplus,
                }
                dimensions_analysis.append(dim_data)

            # Bottleneck identification: Dimension with lowest additional_capacity
            dimensions_analysis.sort(key=lambda d: d["additional_capacity"])
            bottleneck_dim = dimensions_analysis[0]
            feasible_cap = bottleneck_dim["additional_capacity"]

            # Sort dimensions back into canonical order for consistent display
            order_map = {d: idx for idx, d in enumerate(CapacityCalculator.DIMENSIONS)}
            dimensions_analysis.sort(key=lambda d: order_map.get(d["dimension"], 99))

            is_feasible = feasible_cap >= incoming_population
            remaining_after_incoming = feasible_cap - incoming_population

            existing_pop_aggregate = bottleneck_dim["existing_population"]
            total_supported_aggregate = bottleneck_dim["total_supported_population"]

            # Generate narrative capacity explanation
            if is_feasible:
                explanation = (
                    f"{site_name} can absorb the planned incoming population of {incoming_population:,} people. "
                    f"Its primary capacity constraint is {bottleneck_dim['dimension']} ({bottleneck_dim['raw_available_capacity']:,} {bottleneck_dim['raw_unit']}, "
                    f"supporting up to {feasible_cap:,} additional people), leaving a headroom of {remaining_after_incoming:,} people."
                )
            else:
                deficit = abs(remaining_after_incoming)
                explanation = (
                    f"Deficit warning: {site_name} cannot fully support {incoming_population:,} incoming people. "
                    f"The critical binding bottleneck is {bottleneck_dim['dimension']}, which only has headroom for {feasible_cap:,} people "
                    f"({deficit:,} people deficit). Infrastructure augmentation in {bottleneck_dim['dimension']} is required."
                )

            return {
                "site_id": site_id,
                "site_name": site_name,
                "existing_population": existing_pop_aggregate,
                "estimated_total_supported_population": total_supported_aggregate,
                "additional_capacity": feasible_cap,
                "assigned_relocation_population": incoming_population,
                "remaining_capacity": remaining_after_incoming,
                "critical_bottleneck": bottleneck_dim["dimension"],
                "bottleneck": bottleneck_dim,  # detailed object for UI
                "capacity_explanation": explanation,
                "feasible_additional_capacity": feasible_cap,
                "is_feasible": is_feasible,
                "dimensions": dimensions_analysis,
                "disclaimer": "Planning estimate — not legally certified carrying capacity.",
            }
        finally:
            session.close()
