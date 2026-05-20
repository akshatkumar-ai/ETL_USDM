CLASS_QUERY_MAP = {

    # =====================================================
    # CORE STUDY
    # =====================================================

    "study_core":
        """
        study title protocol synopsis study rationale
        protocol version protocol description
        study overview sponsor protocol name
        """,

    "study_definition_document":
        """
        protocol document version approval date
        protocol amendment date governance date
        protocol metadata document references
        """,

    "study_titles":
        """
        official title brief title protocol title
        public title scientific title study title
        """,

    "study_identifiers":
        """
        protocol number study identifier trial identifier
        NCT number EudraCT identifier sponsor identifier
        reference identifier
        """,

    # =====================================================
    # ORGANIZATIONS
    # =====================================================

    "organizations":
        """
        sponsor organization CRO institution site organization
        legal address organization details sponsor information
        """,

    "study_roles":
        """
        investigator sponsor medical monitor study chair
        role responsibilities study personnel
        """,

    "study_sites":
        """
        study sites clinical sites participating centers
        recruiting sites institutions geographic locations
        """,

    # =====================================================
    # AMENDMENTS
    # =====================================================

    "study_amendments":
        """
        protocol amendment amendment rationale protocol changes
        amendment impact amendment history protocol revisions
        enrollment changes study modifications
        """,

    # =====================================================
    # INTERVENTIONS
    # =====================================================

    "study_interventions":
        """
        intervention treatment investigational product
        dosage administration route frequency duration
        placebo comparator therapy dosing regimen
        """,

    "administrable_products":
        """
        drug product formulation dosage form ingredients
        active substance strength excipients product properties
        pharmacologic class medicinal product
        """,

    "medical_devices":
        """
        medical device device identifier device model
        device manufacturer device usage
        """,

    # =====================================================
    # DICTIONARIES
    # =====================================================

    "dictionaries":
        """
        coding dictionary MedDRA WHODrug SNOMED CDISC
        syntax template parameter mapping terminology
        """,

    # =====================================================
    # CONDITIONS
    # =====================================================

    "conditions":
        """
        disease condition diagnosis indication disorder
        target disease inclusion diagnosis
        """,

    "biospecimen_retentions":
        """
        biospecimen sample retention biological samples
        specimen storage tissue banking sample handling
        """,

    "biomedical_concepts":
        """
        biomedical concept assessment measurement endpoint
        clinical concept observation response code
        """,

    "biomedical_concept_categories":
        """
        biomedical concept category concept grouping
        assessment categories clinical domains
        """,

    "biomedical_concept_surrogates":
        """
        surrogate biomarkers surrogate endpoints
        predictive biomarkers clinical surrogates
        """,

    # =====================================================
    # NARRATIVES
    # =====================================================

    "narrative_contents":
        """
        narrative descriptions protocol narrative
        study narrative clinical narrative
        textual descriptions
        """,

    # =====================================================
    # STUDY DESIGN
    # =====================================================

    "study_designs":
        """
        study design randomized blinded parallel crossover
        interventional study observational study
        allocation masking treatment assignment
        study phase
        """,

    # =====================================================
    # STRUCTURE
    # =====================================================

    "epochs":
        """
        screening treatment follow-up maintenance washout
        study periods epochs study phases
        """,

    "arms":
        """
        treatment arms study arms intervention groups
        randomization groups cohorts placebo arm
        active comparator
        """,

    "elements":
        """
        study elements transitions sequence of treatment
        study flow transition rules
        """,

    "study_cells":
        """
        arm epoch combinations study cells
        treatment path combinations
        """,

    "scheduled_instances":
        """
        scheduled visits planned visits visit schedule
        scheduled assessments
        """,

    "encounters":
        """
        clinic visits encounters patient visits
        study visits follow-up visits assessment visits
        contact visits visit windows
        """,

    "schedule_timelines":
        """
        schedule of assessments timeline visit schedule
        timing windows protocol schedule
        assessment schedule visit timeline
        """,

    # =====================================================
    # ACTIVITIES
    # =====================================================

    "activities":
        """
        study activities assessments procedures evaluations
        clinical procedures protocol activities
        """,

    "activity_efficacy":
        """
        efficacy assessments MADRS HAM-A CGI-S
        Q-LES-Q efficacy endpoints depression scales
        clinical outcome measures
        """,

    "activity_eligibility_screening":
        """
        screening assessments inclusion exclusion
        SCID AUDIT DUDIT C-SSRS eligibility procedures
        screening procedures psychiatric evaluation
        """,

    "activity_safety_monitoring":
        """
        safety monitoring adverse events labs ECG
        vital signs pregnancy test concomitant medications
        physical examination safety assessments
        """,

    "activity_abuse_liability":
        """
        abuse liability substance abuse AUDIT DUDIT
        substance use assessment addiction evaluation
        """,

    "activity_solicited_ae_monitoring":
        """
        solicited adverse events nausea headache overdose
        blood pressure heart rate suicidal ideation
        visual effects monitoring
        """,

    "activity_unsolicited_ae_reporting":
        """
        unsolicited adverse events SAE reporting
        serious adverse event reporting
        pharmacovigilance
        """,

    "activity_intervention_administration":
        """
        dosing administration randomization oral dose
        treatment administration investigational product dosing
        """,

    "activity_sas_protocol":
        """
        preparation sessions integration sessions dosing session
        psychedelic assisted therapy support sessions
        psychotherapy protocol
        """,

    # =====================================================
    # OBJECTIVES
    # =====================================================

    "objectives":
        """
        primary objective secondary objective exploratory objective
        primary endpoint secondary endpoint outcome measures
        efficacy endpoints safety endpoints
        """,

    # =====================================================
    # ESTIMANDS
    # =====================================================

    "estimands":
        """
        estimand intercurrent event treatment policy
        hypothetical strategy composite strategy
        analysis population variable of interest
        """,

    # =====================================================
    # POPULATION
    # =====================================================

    "population":
        """
        study population enrolled subjects target population
        sample size demographics cohorts healthy subjects
        planned enrollment
        """,

    "analysis_populations":
        """
        ITT PP safety population analysis set
        modified intent to treat per protocol
        efficacy population
        """,

    # =====================================================
    # ELIGIBILITY
    # =====================================================

    "eligibility_criteria":
        """
        inclusion criteria exclusion criteria eligibility criteria
        participant eligibility enrollment criteria
        subject selection
        """,

    # =====================================================
    # INDICATIONS
    # =====================================================

    "indications":
        """
        indication major depressive disorder MDD
        treatment indication disease indication
        therapeutic indication
        """
}