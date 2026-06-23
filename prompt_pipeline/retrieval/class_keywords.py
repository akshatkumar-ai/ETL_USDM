# retrieval/class_keywords.py
#
# Maps every USDM class (base + custom extension) to a list of
# domain-specific keywords / phrases used by the scorer to judge
# whether a text chunk is relevant to that class.
#
# Rules for maintaining this file:
#   - Prefer short, unambiguous phrases over single generic words.
#   - Include both full forms and abbreviations (e.g. "FDA" + "Food and Drug").
#   - Do NOT add stop-words or purely grammatical tokens.
#   - Custom extension classes live in the second section below.

CLASS_KEYWORDS: dict[str, list[str]] = {

    # ──────────────────────────────────────────────────────────────────────────
    # BASE USDM CLASSES
    # ──────────────────────────────────────────────────────────────────────────

    "study": [
        "study", "trial", "protocol", "study code", "study name",
        "study number", "protocol number", "study title",
    ],

    "studyVersion": [
        "version", "protocol version", "amendment", "rationale",
        "study version", "effective date", "version identifier",
    ],

    "studyTitle": [
        "title", "full title", "official title", "abbreviated title",
        "short title", "acronym", "study name", "trial name",
    ],

    "studyIdentifier": [
        "NCT", "identifier", "registry", "EudraCT", "ISRCTN",
        "ClinicalTrials.gov", "study code", "protocol number",
        "IND number", "registration", "study identifier",
    ],

    "referenceIdentifier": [
        "reference", "cross-reference", "referenced document",
        "referenced protocol", "ClinicalTrials.gov identifier",
        "regulatory reference",
    ],

    "indication": [
        "indication", "disease", "condition", "diagnosis",
        "disorder", "major depressive disorder", "MDD",
        "multiple myeloma", "cancer", "tumor", "malignancy",
        "therapeutic area", "rare disease", "therapeutic indication",
    ],

    "objective": [
        "objective", "primary objective", "secondary objective",
        "exploratory objective", "aim", "goal", "purpose",
        "the study is designed to", "the primary objective",
        "the secondary objective", "to evaluate", "to assess",
        "to determine",
    ],

    "endpoint": [
        "endpoint", "outcome", "primary endpoint", "secondary endpoint",
        "measure", "assessment", "MADRS", "PFS", "OS",
        "overall survival", "progression-free survival",
        "response rate", "remission", "primary outcome measure",
        "secondary outcome measure", "exploratory endpoint",
    ],

    "studyDesign": [
        "study design", "trial design", "randomized", "double-blind",
        "open-label", "placebo-controlled", "phase", "multicenter",
        "crossover", "parallel group", "single-arm", "blinded",
        "interventional", "observational",
    ],

    "interventionalStudyDesign": [
        "randomized", "interventional", "controlled", "blinding",
        "double-blind", "open-label", "parallel", "crossover",
        "dose escalation", "3+3 design", "Bayesian",
    ],

    "observationalStudyDesign": [
        "observational", "cohort", "registry", "prospective",
        "retrospective", "case-control", "cross-sectional",
    ],

    "studyArm": [
        "arm", "group", "cohort", "treatment group", "control group",
        "placebo arm", "active arm", "experimental arm",
        "comparator arm", "arm A", "arm B", "arm C",
        "randomization arm",
    ],

    "studyEpoch": [
        "period", "epoch", "screening period", "treatment period",
        "follow-up period", "run-in", "washout period",
        "induction phase", "maintenance phase", "consolidation phase",
        "preparation period", "dosing period",
    ],

    "studyCell": [
        "study cell", "schedule matrix", "treatment cell",
    ],

    "studyElement": [
        "element", "study element", "treatment element",
        "transition rule", "start rule", "end rule",
    ],

    "eligibilityCriterion": [
        "inclusion", "exclusion", "criteria", "eligible", "eligibility",
        "must have", "must not", "patients who", "subjects who",
        "inclusion criteria", "exclusion criteria", "key eligibility",
        "not eligible", "eligible if",
    ],

    "studyDesignPopulation": [
        "population", "sample size", "enrollment", "planned enrollment",
        "number of patients", "number of subjects",
        "intent-to-treat", "ITT", "per protocol",
        "safety population", "planned number", "enrolled",
    ],

    "populationDefinition": [
        "population definition", "planned sex", "age range",
        "healthy subjects", "planned age", "completion number",
        "enrollment number", "males and females",
    ],

    "encounter": [
        "visit", "day", "assessment visit", "screening visit",
        "baseline visit", "follow-up visit", "dosing day",
        "contact", "clinic visit", "outpatient", "inpatient",
        "study day", "day 1", "day 8", "day 15",
    ],

    "activity": [
        "activity", "procedure", "assessment", "laboratory",
        "blood draw", "ECG", "vital signs", "physical examination",
        "questionnaire", "biopsy", "PK sampling", "imaging",
        "urine drug screen",
    ],

    "scheduleTimeline": [
        "schedule", "timeline", "schedule of activities", "study calendar",
        "visit schedule", "assessment schedule",
        "schedule of assessments", "main timeline",
    ],

    "timing": [
        "timing", "window", "days before", "days after",
        "relative to", "prior to", "post dose", "at least",
        "no later than", "within", "between", "day 1",
        "plus or minus", "±", "visit window",
    ],

    "scheduleTimelineExit": [
        "end of study", "early termination", "withdrawal",
        "last visit", "exit", "discontinuation",
    ],

    "studyIntervention": [
        "intervention", "drug", "treatment", "investigational product",
        "IP", "IMP", "medication", "compound", "agent",
        "psilocybin", "niacin", "cilta-cel", "talquetamab",
        "daratumumab", "lenalidomide", "bortezomib", "dexamethasone",
        "ciltacabtagene", "erdafitinib", "doxorubicin", "KENDO",
    ],

    "administrableProduct": [
        "capsule", "tablet", "vial", "formulation", "dosage form",
        "oral solid", "injectable", "infusion bag",
        "HPMC capsule", "HDPE bottle", "dose form",
    ],

    "administration": [
        "dose", "dosing", "mg", "mg/kg", "mg/m2", "route",
        "intravenous", "oral", "subcutaneous", "frequency",
        "once daily", "weekly", "Q2W", "Q3W", "Q4W",
        "administration", "infusion", "injection",
    ],

    "strength": [
        "strength", "concentration", "mg/mL", "unit dose",
        "numerator", "denominator", "dose strength",
    ],

    "substance": [
        "substance", "active ingredient", "active substance",
        "INN", "chemical name", "drug substance",
    ],

    "ingredient": [
        "ingredient", "excipient", "active moiety",
        "drug product component",
    ],

    "estimand": [
        "estimand", "intercurrent event", "treatment policy",
        "hypothetical strategy", "principal stratum",
        "composite strategy", "variable of interest",
        "population of interest",
    ],

    "intercurrentEvent": [
        "intercurrent event", "dropout", "discontinuation",
        "death", "rescue medication", "treatment switch",
    ],

    "analysisPopulation": [
        "intent-to-treat", "ITT", "full analysis set", "FAS",
        "per protocol", "PP", "safety population",
        "modified ITT", "evaluable population", "randomized set",
        "all treated",
    ],

    "studyAmendment": [
        "amendment", "protocol amendment", "protocol modification",
        "change", "revision", "version history",
        "substantial amendment", "non-substantial",
    ],

    "studyChange": [
        "change", "study change", "protocol change",
        "modification rationale", "reason for change",
    ],

    "Organization": [
        "sponsor", "organization", "company", "institute",
        "CRO", "contract research", "funder", "manufacturer",
        "Usona", "BMT CTN", "Emmes", "CIBMTR", "Anthropic",
    ],

    "address": [
        "address", "street", "city", "state", "zip", "postal code",
        "country", "location",
    ],

    "studyRole": [
        "principal investigator", "PI", "co-PI", "co-investigator",
        "medical monitor", "sponsor representative",
        "study coordinator", "sub-investigator",
    ],

    "studySite": [
        "site", "center", "institution", "investigational site",
        "clinical site", "transplant center", "hospital",
    ],

    "GeographicScope": [
        "geographic scope", "country", "region", "global",
        "United States", "European Union", "multinational",
    ],

    "GovernanceDate": [
        "date", "effective date", "approval date", "submission date",
        "protocol date", "signature date",
    ],

    "BiomedicalConcept": [
        "biomedical concept", "assessment", "measurement",
        "clinical concept", "MADRS", "LVEF", "RECIST",
        "laboratory test", "vital sign",
    ],

    "BiomedicalConceptCategory": [
        "category", "domain", "biomedical category",
        "clinical domain", "safety domain",
    ],

    "Procedure": [
        "procedure", "clinical procedure", "echocardiogram",
        "MUGA", "ECG", "PK sampling", "biopsy",
        "physical examination", "urine drug screen",
    ],

    "narrativeContent": [
        "section", "narrative", "synopsis section",
        "document section", "protocol section",
    ],

    "BiospecimenRetention": [
        "biospecimen", "sample", "retained", "DNA", "tissue",
        "blood sample", "biopsy sample", "biobank",
    ],

    "syntaxTemplate": [
        "template", "syntax", "text template", "parameter",
    ],

    "DocumentContentReference": [
        "section number", "section title", "document reference",
        "cross-reference", "appendix",
    ],

    # ──────────────────────────────────────────────────────────────────────────
    # CUSTOM EXTENSION CLASSES
    # ──────────────────────────────────────────────────────────────────────────

    "statisticalAnalysis": [
        "statistical", "power", "sample size", "alpha", "type I error",
        "MMRM", "mixed model", "ANCOVA", "repeated measures",
        "effect size", "hypothesis", "significance",
        "confidence interval", "two-sided", "one-sided",
        "dropout rate", "attrition", "80%", "85%", "90%",
        "92%", "98%", "powered to detect",
    ],

    "randomization": [
        "randomization", "randomized", "randomise", "allocation",
        "stratification", "stratified", "1:1", "2:2:1",
        "allocation ratio", "block randomization",
        "stratification factor", "blinding", "double-blind",
        "open-label", "unblinding", "randomization scheme",
    ],

    "concomitantMedications": [
        "concomitant", "prohibited", "allowed medications",
        "permitted medications", "washout", "half-life",
        "prior medication", "background therapy", "taper",
        "medication taper", "benzodiazepine", "antidepressant",
        "stop at least", "5x the elimination",
    ],

    "dataMonitoringCommittee": [
        "DSMB", "DMC", "data safety monitoring board",
        "data monitoring committee", "independent monitoring",
        "safety review committee", "interim analysis",
        "stopping rules", "safety oversight",
    ],

    "regulatorySubmissions": [
        "FDA", "EMA", "regulatory", "submission", "IND",
        "CTA", "NDA", "BLA", "MAA", "regulatory approval",
        "SAE reporting", "adverse event reporting",
        "FDA guidelines", "per FDA", "regulatory requirements",
    ],

    "documentClassification": [
        "confidential", "classification", "proprietary",
        "restricted", "not for distribution", "internal use only",
    ],

    "urineDrugScreenPanel": [
        "urine drug screen", "drug test", "UDS", "drug panel",
        "toxicology screen", "amphetamine", "cocaine", "cannabis",
        "opiates", "benzodiazepines", "THC", "MDMA", "methadone",
        "phencyclidine", "PCP", "buprenorphine", "barbiturates",
    ],

    "psychologicalSupportProtocol": [
        "set and setting", "facilitator", "preparation session",
        "integration session", "psychological support",
        "therapeutic context", "psychedelic session",
        "dosing session", "therapist", "guide", "SaS protocol",
    ],

    "labValueThresholds": [
        "threshold", "laboratory value", "lab value",
        "normal range", "QTcF", "blood pressure", "SBP", "DBP",
        "heart rate", "MADRS score", "Child-Pugh",
        "creatinine", "ALT", "AST", "hemoglobin", "platelets",
        "ANC", "LVEF", "ejection fraction", "bilirubin",
        "mmHg", "milliseconds", "beats per minute",
    ],

    "cellTherapyManufacturing": [
        "leukapheresis", "apheresis", "manufacturing", "CAR T",
        "cell therapy", "chimeric antigen receptor",
        "manufacturing site", "product release", "vein to vein",
        "cilta-cel", "ciltacabtagene", "BCMA CAR",
        "T-cell product", "cell product",
    ],

    "lymphodepletingChemotherapy": [
        "lymphodepletion", "lymphodepleting", "conditioning regimen",
        "fludarabine", "cyclophosphamide", "Cy/Flu",
        "preparative regimen", "before CAR T infusion",
        "prior to infusion", "lymphodepleting chemotherapy",
    ],

    "stepUpDosingSchedules": [
        "step-up", "step up dosing", "escalation",
        "ramp-up dosing", "dose escalation", "fractionated dosing",
        "initial dose", "escalating dose", "priming dose",
        "0.01 mg", "0.06 mg", "talquetamab step",
    ],

    "diseaseRiskDefinitions": [
        "risk", "staging", "R-ISS", "ISS", "cytogenetics",
        "high-risk", "del(17p)", "t(4:14)", "t(14:16)", "1q21",
        "GEP70", "SKY92", "TP53", "c-Myc", "extramedullary",
        "FDG PET", "circulating plasma cells",
        "risk stratification", "high risk features",
    ],

    "minimalResidualDiseaseAssessment": [
        "MRD", "minimal residual disease", "MRD negativity",
        "MRD negative", "sustained MRD", "deep response",
        "next-generation sequencing", "flow cytometry",
        "MRD threshold", "undetectable MRD",
    ],

    "biomarkerDefinitions": [
        "biomarker", "BCMA", "GPRC5D", "expression", "genomic",
        "GEP70", "SKY92", "CAR T expansion", "CAR T persistence",
        "immune reconstitution", "pharmacodynamic",
        "target expression", "B cell maturation antigen",
    ],

    "immuneMediatedToxicityMonitoring": [
        "CRS", "cytokine release syndrome", "neurotoxicity",
        "ICANS", "immune effector cell", "immune-mediated",
        "ASTCT", "cytokine storm", "immune toxicity",
        "neurotoxicity grading", "grade 3 CRS",
    ],

    "priorTherapyRequirements": [
        "prior therapy", "prior treatment", "induction therapy",
        "previous treatment", "Dara-RVd", "prior systemic",
        "prior lines", "treatment naive", "at least 4 cycles",
        "cycles of induction", "prior chemotherapy",
        "no prior progression",
    ],

    "stemCellCollectionRequirements": [
        "stem cell", "CD34", "apheresis collection",
        "peripheral blood stem cell", "PBSC",
        "mobilization", "stem cell yield", "cells/kg",
        "10e6", "transplant eligible", "stem cell harvest",
        "at least two autologous",
    ],

    "accrualObjective": [
        "accrual", "enrollment target", "accrual rate",
        "accrual period", "recruitment", "target enrollment",
        "number of patients", "planned enrollment",
        "accrual objective", "185 patients", "100 patients",
        "74 patients", "37 patients",
    ],

    "siteManagement": [
        "sites", "centers", "institutions", "multi-site",
        "number of sites", "target sites", "study sites",
        "participating sites", "30 sites", "investigational sites",
        "site selection", "site initiation",
    ],

    "longTermFollowUp": [
        "long-term follow-up", "LTFU", "long term follow up",
        "15 years", "10 years", "regulatory requirements",
        "CIBMTR", "registry follow-up", "survival follow-up",
        "long-term outcomes", "late effects",
        "years to meet regulatory",
    ],
}