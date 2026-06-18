# prompt_pipeline/subsection.py
#
# Responsible for extracting a focused JSON sub-schema for a single USDM class.
# The LLM only ever sees the slice of the schema it needs to fill — this keeps
# prompts tight and outputs parseable.
#
# Two registries live here:
#   USDM_CLASS_PATHS       — base USDM classes mapped to their JSON path
#                            inside the master usdm_schema.json template
#   CUSTOM_CLASS_SCHEMAS   — extension classes that have no path in the base
#                            template; their schema is defined inline here

from __future__ import annotations

import copy
import json
from typing import Any, Dict, List, Optional, Union


# ── BASE USDM CLASS → JSON PATH ────────────────────────────────────────────────
# Paths use a mix of string keys and integer indexes (for lists).
# An integer means "first element of this array".

USDM_CLASS_PATHS: Dict[str, List[Union[str, int]]] = {

    # Top-level study
    "study":
        ["study"],

    "studyVersion":
        ["study", "versions"],

    "studyTitle":
        ["study", "versions", 0, "titles"],

    "studyIdentifier":
        ["study", "versions", 0, "studyIdentifiers"],

    "referenceIdentifier":
        ["study", "versions", 0, "referenceIdentifiers"],

    # Study design — common
    "studyDesign":
        ["study", "versions", 0, "studyDesigns"],

    "interventionalStudyDesign":
        ["study", "versions", 0, "studyDesigns"],

    "observationalStudyDesign":
        ["study", "versions", 0, "studyDesigns"],

    # Within studyDesign[0]
    "indication":
        ["study", "versions", 0, "studyDesigns", 0, "indications"],

    "objective":
        ["study", "versions", 0, "studyDesigns", 0, "objectives"],

    "endpoint":
        ["study", "versions", 0, "studyDesigns", 0, "objectives", 0, "endpoints"],

    "estimand":
        ["study", "versions", 0, "studyDesigns", 0, "estimands"],

    "intercurrentEvent":
        ["study", "versions", 0, "studyDesigns", 0, "estimands", 0, "intercurrentEvents"],

    "studyArm":
        ["study", "versions", 0, "studyDesigns", 0, "arms"],

    "studyEpoch":
        ["study", "versions", 0, "studyDesigns", 0, "epochs"],

    "studyCell":
        ["study", "versions", 0, "studyDesigns", 0, "studyCells"],

    "studyElement":
        ["study", "versions", 0, "studyDesigns", 0, "elements"],

    "eligibilityCriterion":
        ["eligibilityCriteria"],                               # top-level in schema

    "studyDesignPopulation":
        ["study", "versions", 0, "studyDesigns", 0, "population"],

    "populationDefinition":
        ["study", "versions", 0, "studyDesigns", 0, "population"],

    "encounter":
        ["study", "versions", 0, "studyDesigns", 0, "encounters"],

    "activity":
        ["study", "versions", 0, "studyDesigns", 0, "activities"],

    "scheduleTimeline":
        ["scheduleTimelines"],                                  # top-level in schema

    "timing":
        ["study", "versions", 0, "studyDesigns", 0, "timings"],

    "scheduleTimelineExit":
        ["study", "versions", 0, "studyDesigns", 0, "scheduleTimelineExits"],

    "studyIntervention":
        ["studyInterventions"],                                 # top-level in schema

    "administrableProduct":
        ["administrableProducts"],                              # top-level in schema

    "administration":
        ["study", "versions", 0, "studyDesigns", 0, "administrations"],

    "strength":
        ["study", "versions", 0, "studyDesigns", 0, "strengths"],

    "substance":
        ["study", "versions", 0, "studyDesigns", 0, "substances"],

    "BiomedicalConcept":
        ["biomedicalConcepts"],                                 # top-level in schema

    "BiomedicalConceptCategory":
        ["bcCategories"],

    "Procedure":
        ["study", "versions", 0, "studyDesigns", 0, "procedures"],

    "BiospecimenRetention":
        ["study", "versions", 0, "studyDesigns", 0, "biospecimenRetentions"],

    "analysisPopulation":
        ["analysisPopulations"],                                # top-level in schema

    "studyAmendment":
        ["study", "versions", 0, "amendments"],

    "studyChange":
        ["study", "versions", 0, "studyChanges"],

    "Organization":
        ["organizations"],                                      # top-level in schema

    "address":
        ["organizations", 0, "legalAddress"],

    "studyRole":
        ["study", "versions", 0, "studyRoles"],

    "studySite":
        ["study", "versions", 0, "studySites"],

    "GeographicScope":
        ["study", "versions", 0, "geographicScopes"],

    "GovernanceDate":
        ["study", "versions", 0, "dateValues"],

    "narrativeContent":
        ["documentedBy"],

    "DocumentContentReference":
        ["documentedBy", 0, "documentContentReferences"],

    "syntaxTemplate":
        ["study", "versions", 0, "studyDesigns", 0, "syntaxTemplates"],

    "dictionaries":
        ["dictionaries"],

    "conditions":
        ["conditions"],

    "notes":
        ["notes"],
}


# ── CUSTOM EXTENSION CLASS SCHEMAS ─────────────────────────────────────────────
# Classes that have no path in usdm_schema.json.
# Each entry is the schema template that the LLM should populate.
# They will be placed at the appropriate nesting level during final merge.

CUSTOM_CLASS_SCHEMAS: Dict[str, Any] = {

    "statisticalAnalysis": {
        "id": None,
        "name": None,
        "label": None,
        "description": None,
        "primaryModel": None,
        "analysisSet": None,
        "sampleSizeJustification": {
            "id": None,
            "plannedEnrollment": None,
            "dropoutRate": None,
            "assumptions": [
                {
                    "id": None,
                    "parameter": None,
                    "value": None,
                    "unit": None,
                    "timepoint": None,
                    "effectSize": None,
                    "source": None
                }
            ],
            "powerEstimates": [
                {
                    "id": None,
                    "endpoint": None,
                    "endpointId": None,
                    "power": None,
                    "sampleSize": None,
                    "alpha": None
                }
            ]
        }
    },

    "randomization": {
        "id": None,
        "name": None,
        "label": None,
        "description": None,
        "ratio": None,
        "ratioDescription": None,
        "type": None,
        "blindingSchema": None,
        "blindingNotes": None,
        "stratificationFactors": [
            {
                "id": None,
                "name": None,
                "label": None,
                "description": None,
                "levels": None
            }
        ]
    },

    "concomitantMedications": {
        "id": None,
        "name": None,
        "label": None,
        "description": None,
        "generalWashoutRule": None,
        "permitted": [
            {
                "id": None,
                "name": None,
                "description": None,
                "condition": None
            }
        ],
        "taperedBeforeBaseline": [
            {
                "id": None,
                "name": None,
                "description": None,
                "taperSupervisor": None,
                "minimumWashout": None
            }
        ],
        "suspendedBeforeDosing": [
            {
                "id": None,
                "name": None,
                "description": None,
                "minimumSuspensionWindow": None
            }
        ],
        "prohibited": [
            {
                "id": None,
                "name": None,
                "description": None,
                "washoutRule": None
            }
        ]
    },

    "dataMonitoringCommittee": {
        "id": None,
        "name": None,
        "label": None,
        "description": None,
        "type": None,
        "mandate": None,
        "composition": None,
        "charter": None,
        "reviewFrequency": None
    },

    "regulatorySubmissions": [
        {
            "id": None,
            "name": None,
            "label": None,
            "agencyName": None,
            "agencyAbbreviation": None,
            "country": None,
            "submissionType": None,
            "safetyReportingStandard": None,
            "registryIdentifier": None,
            "registryName": None
        }
    ],

    "documentClassification": {
        "id": None,
        "confidentialityLevel": None,
        "label": None,
        "notes": None
    },

    "urineDrugScreenPanel": {
        "id": None,
        "name": None,
        "label": None,
        "description": None,
        "substances": [],
        "exceptions": [
            {
                "substance": None,
                "exceptionCondition": None
            }
        ],
        "administeredAt": [],
        "notes": None
    },

    "psychologicalSupportProtocol": {
        "id": None,
        "name": None,
        "label": None,
        "description": None,
        "applicability": None,
        "setting": None,
        "components": [
            {
                "id": None,
                "sequence": None,
                "name": None,
                "description": None,
                "timing": None,
                "facilitatorCount": None,
                "sessionCount": None
            }
        ]
    },

    "labValueThresholds": [
        {
            "id": None,
            "name": None,
            "label": None,
            "test": None,
            "excludeIfValue": None,
            "includeIfValue": None,
            "recordIfValue": None,
            "interpretation": None,
            "linkedCriterionId": None
        }
    ],

    "cellTherapyManufacturing": [
        {
            "id": None,
            "name": None,
            "label": None,
            "description": None,
            "productId": None,
            "productName": None,
            "collectionProcedure": None,
            "collectionTiming": None,
            "collectionArms": [],
            "targetAntigen": None,
            "vectorType": None,
            "minimumStemCellYield": None,
            "manufacturingNotes": None
        }
    ],

    "lymphodepletingChemotherapy": [
        {
            "id": None,
            "name": None,
            "label": None,
            "description": None,
            "applicableArms": [],
            "timing": None,
            "agents": [
                {
                    "id": None,
                    "interventionId": None,
                    "name": None,
                    "dose": None,
                    "frequency": None,
                    "durationDays": None
                }
            ]
        }
    ],

    "stepUpDosingSchedules": [
        {
            "id": None,
            "name": None,
            "label": None,
            "description": None,
            "interventionId": None,
            "interventionName": None,
            "applicableArms": [],
            "steps": [
                {
                    "id": None,
                    "stepNumber": None,
                    "dose": None,
                    "unit": None,
                    "numericDose": None
                }
            ],
            "maintenanceDose": None,
            "maintenanceFrequency": None,
            "maintenanceDuration": None,
            "notes": None
        }
    ],

    "diseaseRiskDefinitions": [
        {
            "id": None,
            "name": None,
            "label": None,
            "description": None,
            "indicationId": None,
            "stagingSystem": None,
            "riskTier": None,
            "criteria": [
                {
                    "id": None,
                    "name": None,
                    "type": None,
                    "value": None,
                    "text": None,
                    "standalone": None
                }
            ]
        }
    ],

    "minimalResidualDiseaseAssessment": [
        {
            "id": None,
            "name": None,
            "label": None,
            "description": None,
            "endpointId": None,
            "definition": None,
            "assessmentMethod": None,
            "sensitivityThreshold": None,
            "sustainedDefinition": None,
            "notes": None
        }
    ],

    "biomarkerDefinitions": [
        {
            "id": None,
            "name": None,
            "label": None,
            "description": None,
            "target": None,
            "purpose": None,
            "endpointId": None,
            "assessmentMethod": None,
            "sampleType": None
        }
    ],

    "immuneMediatedToxicityMonitoring": [
        {
            "id": None,
            "name": None,
            "label": None,
            "description": None,
            "toxicityType": None,
            "gradingSystem": None,
            "endpointId": None,
            "monitoringPeriod": None,
            "applicableInterventions": [],
            "notes": None
        }
    ],

    "priorTherapyRequirements": [
        {
            "id": None,
            "name": None,
            "label": None,
            "description": None,
            "minimumCycles": None,
            "regimen": None,
            "regimenComponents": [],
            "regimenAbbreviation": None,
            "prohibitedPriorEvents": None,
            "linkedCriterionIds": []
        }
    ],

    "stemCellCollectionRequirements": [
        {
            "id": None,
            "name": None,
            "label": None,
            "description": None,
            "collectionType": None,
            "minimumYield": None,
            "minimumYieldNumeric": None,
            "minimumYieldUnit": None,
            "rationaleForMinimum": None,
            "timing": None,
            "linkedCriterionId": None
        }
    ],

    "accrualObjective": {
        "id": None,
        "name": None,
        "label": None,
        "description": None,
        "totalPlannedEnrollment": None,
        "accrualPeriod": None,
        "targetNumberOfSites": None,
        "armAllocation": [
            {
                "armId": None,
                "armName": None,
                "plannedN": None,
                "randomizationWeight": None
            }
        ],
        "notes": None
    },

    "siteManagement": {
        "id": None,
        "name": None,
        "label": None,
        "targetNumberOfSites": None,
        "targetNumberOfSitesLabel": None,
        "accrualPeriod": None,
        "siteType": None,
        "notes": None
    },

    "longTermFollowUp": {
        "id": None,
        "name": None,
        "label": None,
        "description": None,
        "duration": None,
        "durationUnit": None,
        "regulatoryBasis": None,
        "infrastructure": None,
        "infrastructureId": None,
        "protocol": None,
        "notes": None
    },
}


# ── ALL KNOWN CLASSES (base + custom) ─────────────────────────────────────────

ALL_USDM_CLASSES: List[str] = (
    list(USDM_CLASS_PATHS.keys()) + list(CUSTOM_CLASS_SCHEMAS.keys())
)


# ── Template loading ───────────────────────────────────────────────────────────

def load_template(template_path: str) -> Dict:
    with open(template_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Path helpers ───────────────────────────────────────────────────────────────

def get_nested_value(data: Any, path: List[Union[str, int]]) -> Optional[Any]:
    current = data
    for key in path:
        if isinstance(key, int):
            if isinstance(current, list) and len(current) > key:
                current = current[key]
            else:
                return None
        else:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
    return current


def set_nested_value(
    data: Any,
    path: List[Union[str, int]],
    value: Any,
) -> None:
    current = data
    for i, key in enumerate(path[:-1]):
        next_key = path[i + 1]
        if isinstance(key, int):
            while len(current) <= key:
                current.append({})
            current = current[key]
        else:
            if key not in current:
                current[key] = [] if isinstance(next_key, int) else {}
            current = current[key]

    final_key = path[-1]
    if isinstance(final_key, int):
        while len(current) <= final_key:
            current.append(None)
        current[final_key] = value
    else:
        current[final_key] = value


# ── Public API ─────────────────────────────────────────────────────────────────

def get_subschema(
    usdm_class: str,
    template_path: str = "/home/riya/USDM/ETL_USDM/template/usdm_schema.json",
) -> Dict:
    """
    Return a minimal JSON sub-schema for one USDM class.

    For base classes: slice the field out of the master template.
    For custom extension classes: return the inline schema defined above.

    The returned dict is what the LLM receives; it must return the same
    structure with values filled in.
    """

    # ── Custom extension class ────────────────────────────────────────────────
    if usdm_class in CUSTOM_CLASS_SCHEMAS:
        return {usdm_class: copy.deepcopy(CUSTOM_CLASS_SCHEMAS[usdm_class])}

    # ── Base USDM class ───────────────────────────────────────────────────────
    if usdm_class not in USDM_CLASS_PATHS:
        # Unknown class — return empty shell so the caller can still proceed
        return {usdm_class: None}

    master = load_template(template_path)
    path   = USDM_CLASS_PATHS[usdm_class]
    value  = get_nested_value(master, path)

    if value is None:
        return {usdm_class: None}

    subschema: Dict = {}
    set_nested_value(subschema, path, copy.deepcopy(value))
    return subschema


# ── Self-test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    for cls_name in ["objective", "eligibilityCriterion", "statisticalAnalysis",
                     "cellTherapyManufacturing", "randomization"]:
        schema = get_subschema(cls_name)
        print(f"\n{'='*60}")
        print(f"Sub-schema for: {cls_name}")
        print(json.dumps(schema, indent=2)[:800])