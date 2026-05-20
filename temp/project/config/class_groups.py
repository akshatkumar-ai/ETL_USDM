CLASS_GROUPS = {

    # =====================================================
    # CORE STUDY METADATA
    # =====================================================

    "study_core": [
        "study",
        "study.studyVersion.versionIdentifier",
        "study.studyVersion.rationale"
    ],

    "study_definition_document": [
        "study.studyVersion.studyDefinitionDocument",
        "study.studyVersion.studyDefinitionDocument.studyDefinitionDocumentVersion",
        "study.studyVersion.studyDefinitionDocument.studyDefinitionDocumentVersion.governanceDates",
        "study.studyVersion.studyDefinitionDocument.studyDefinitionDocumentVersion.documentContentReferences"
    ],

    "study_titles": [
        "study.studyVersion.studyTitles"
    ],

    "study_identifiers": [
        "study.studyVersion.studyIdentifiers",
        "study.studyVersion.referenceIdentifiers"
    ],

    # =====================================================
    # ORGANIZATIONS / SITES / ROLES
    # =====================================================

    "organizations": [
        "study.studyVersion.organizations"
    ],

    "study_roles": [
        "study.studyVersion.studyRoles"
    ],

    "study_sites": [
        "study.studyVersion.studySites"
    ],

    # =====================================================
    # AMENDMENTS
    # =====================================================

    "study_amendments": [
        "study.studyVersion.studyAmendments",
        "study.studyVersion.studyAmendments.enrollments",
        "study.studyVersion.studyAmendments.primaryReason",
        "study.studyVersion.studyAmendments.secondaryReasons",
        "study.studyVersion.studyAmendments.impacts",
        "study.studyVersion.studyAmendments.changes"
    ],

    # =====================================================
    # INTERVENTIONS / PRODUCTS / DEVICES
    # =====================================================

    "study_interventions": [
        "study.studyVersion.studyInterventions",
        "study.studyVersion.studyInterventions.administrations"
    ],

    "administrable_products": [
        "study.studyVersion.administrableProducts",
        "study.studyVersion.administrableProducts.administrableDoseForm",
        "study.studyVersion.administrableProducts.administrableDoseForm.ingredients",
        "study.studyVersion.administrableProducts.administrableDoseForm.properties"
    ],

    "medical_devices": [
        "study.studyVersion.medicalDevices"
    ],

    # =====================================================
    # DICTIONARIES / TEMPLATES
    # =====================================================

    "dictionaries": [
        "study.studyVersion.dictionaries",
        "study.studyVersion.dictionaries.parameterMaps",
        "study.studyVersion.dictionaries.syntaxTemplates"
    ],

    # =====================================================
    # CONDITIONS / BIOMEDICAL CONCEPTS
    # =====================================================

    "conditions": [
        "study.studyVersion.conditions"
    ],

    "biospecimen_retentions": [
        "study.studyVersion.biospecimenRetentions"
    ],

    "biomedical_concepts": [
        "study.studyVersion.biomedicalConcepts",
        "study.studyVersion.biomedicalConcepts.properties"
    ],

    "biomedical_concept_categories": [
        "study.studyVersion.biomedicalConceptCategories"
    ],

    "biomedical_concept_surrogates": [
        "study.studyVersion.biomedicalConceptSurrogates"
    ],

    # =====================================================
    # NARRATIVE CONTENT
    # =====================================================

    "narrative_contents": [
        "study.studyVersion.narrativeContents"
    ],

    # =====================================================
    # STUDY DESIGN
    # =====================================================

    "study_designs": [
        "study.studyVersion.studyDesigns",
        "study.studyVersion.studyDesigns.interventionalStudyDesign",
        "study.studyVersion.studyDesigns.observationalStudyDesign"
    ],

    # =====================================================
    # STRUCTURAL DESIGN COMPONENTS
    # =====================================================

    "epochs": [
        "study.studyVersion.studyDesigns.epochs"
    ],

    "arms": [
        "study.studyVersion.studyDesigns.arms"
    ],

    "elements": [
        "study.studyVersion.studyDesigns.elements"
    ],

    "study_cells": [
        "study.studyVersion.studyDesigns.studyCells"
    ],

    "scheduled_instances": [
        "study.studyVersion.studyDesigns.scheduledInstances"
    ],

    "encounters": [
        "study.studyVersion.studyDesigns.encounters"
    ],

    "schedule_timelines": [
        "study.studyVersion.studyDesigns.scheduleTimelines"
    ],

    # =====================================================
    # ACTIVITIES
    # =====================================================

    "activities": [
        "study.studyVersion.studyDesigns.activities"
    ],

    "activity_efficacy": [
        "study.studyVersion.studyDesigns.activities[0]"
    ],

    "activity_eligibility_screening": [
        "study.studyVersion.studyDesigns.activities[1]"
    ],

    "activity_safety_monitoring": [
        "study.studyVersion.studyDesigns.activities[2]"
    ],

    "activity_abuse_liability": [
        "study.studyVersion.studyDesigns.activities[3]"
    ],

    "activity_solicited_ae_monitoring": [
        "study.studyVersion.studyDesigns.activities[4]"
    ],

    "activity_unsolicited_ae_reporting": [
        "study.studyVersion.studyDesigns.activities[5]"
    ],

    "activity_intervention_administration": [
        "study.studyVersion.studyDesigns.activities[6]"
    ],

    "activity_sas_protocol": [
        "study.studyVersion.studyDesigns.activities[7]"
    ],

    # =====================================================
    # OBJECTIVES / ENDPOINTS
    # =====================================================

    "objectives": [
        "study.studyVersion.studyDesigns.objectives"
    ],

    # =====================================================
    # ESTIMANDS
    # =====================================================

    "estimands": [
        "study.studyVersion.studyDesigns.estimands"
    ],

    # =====================================================
    # POPULATIONS
    # =====================================================

    "population": [
        "study.studyVersion.studyDesigns.population"
    ],

    "analysis_populations": [
        "study.studyVersion.studyDesigns.analysisPopulations"
    ],

    # =====================================================
    # ELIGIBILITY
    # =====================================================

    "eligibility_criteria": [
        "study.studyVersion.studyDesigns.eligibilityCriteria"
    ],

    # =====================================================
    # INDICATIONS
    # =====================================================

    "indications": [
        "study.studyVersion.studyDesigns.indications"
    ]
}