"""Facade Tool Schemas for the EHR Integration Agent.

These schemas define the structured intent interface for the LLM. 
Under the hood, the execution engine maps these to raw Context7 MCP calls.
"""

FHIR_RESOURCE_SPEC_TOOL = {
    "name": "query_fhir_r4_resource",
    "description": "Fetch official FHIR R4 documentation, JSON structures, and element definitions for a specific resource type. Use this to ensure compliance when designing EHR data models.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "resource_type": {
                "type": "string",
                "description": "The exact name of the FHIR resource (e.g., 'Patient', 'Observation', 'Encounter')."
            },
            "element_path": {
                "type": "string",
                "description": "Optional. The specific element path to query within the resource (e.g., 'Patient.identifier' or 'Observation.valueQuantity')."
            },
            "profile": {
                "type": "string",
                "description": "Optional. Specify a localized profile if needed (e.g., 'ABDM_Patient_Profile')."
            }
        },
        "required": ["resource_type"]
    }
}

HL7_SEGMENT_DEFINITION_TOOL = {
    "name": "query_hl7_segment_mapping",
    "description": "Retrieve exact field definitions, data types, and mapping guidelines for HL7 v2.x segments and message types.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "segment_code": {
                "type": "string",
                "description": "The 3-character HL7 segment code (e.g., 'PID', 'OBR', 'IN1')."
            },
            "message_type": {
                "type": "string",
                "description": "Optional. The trigger event or message type (e.g., 'ADT^A01', 'ORM^O01')."
            },
            "hl7_version": {
                "type": "string",
                "enum": ["2.3", "2.3.1", "2.4", "2.5", "2.5.1", "2.6"],
                "default": "2.5.1",
                "description": "The specific HL7 version used by the legacy system."
            }
        },
        "required": ["segment_code"]
    }
}

HEALTHCARE_ML_FRAMEWORK_TOOL = {
    "name": "query_medical_ml_framework",
    "description": "Retrieve architectural guidelines, API references, and best practices for healthcare-specific machine learning frameworks.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "framework": {
                "type": "string",
                "enum": ["MONAI", "TorchIO", "TensorFlow_Health", "BioBERT"],
                "description": "The specific healthcare ML framework being utilized."
            },
            "concept": {
                "type": "string",
                "description": "The architectural concept or component to query (e.g., 'Medical Image Transformation pipelines', 'DICOM loading', 'Clinical NLP fine-tuning')."
            },
            "code_snippet_required": {
                "type": "boolean",
                "default": False,
                "description": "Set to true if implementation code examples are needed for the architecture design."
            }
        },
        "required": ["framework", "concept"]
    }
}

IG_SEMANTIC_SEARCH_TOOL = {
    "name": "search_integration_guidelines",
    "description": "Perform a semantic search across Context7's vector database of implementation guides, policy documents, and interoperability standards.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "search_query": {
                "type": "string",
                "description": "The semantic query (e.g., 'How to implement SMART on FHIR standalone launch' or 'ABDM Health ID (ABHA) creation workflow')."
            },
            "standard_domain": {
                "type": "string",
                "enum": ["ABDM", "SMART_ON_FHIR", "DICOM_WEB", "IHE_PROFILES"],
                "description": "Filter the search to a specific interoperability domain."
            },
            "max_results": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "default": 3,
                "description": "Maximum number of documentation chunks to return."
            }
        },
        "required": ["search_query", "standard_domain"]
    }
}

EHR_INTEGRATION_TOOLS = [
    FHIR_RESOURCE_SPEC_TOOL,
    HL7_SEGMENT_DEFINITION_TOOL,
    HEALTHCARE_ML_FRAMEWORK_TOOL,
    IG_SEMANTIC_SEARCH_TOOL
]
