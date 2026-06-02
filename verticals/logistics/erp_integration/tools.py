"""Facade Tool Schemas for the ERP Integration Agent.

These schemas define the structured intent interface for the LLM. 
Under the hood, the execution engine maps these to raw Context7 MCP calls for Tally Prime and other ERPs.
"""

TALLY_XML_SCHEMA_ENGINE_TOOL = {
    "name": "get_tally_xml_envelope",
    "description": "Fetch the precise XML payload structure required to export or import data from Tally Prime. Use this to ensure formatting compliance for specific request types.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "request_action": {
                "type": "string",
                "enum": ["Export", "Import", "Execute"],
                "description": "The target action type for the Tally XML interface."
            },
            "object_type": {
                "type": "string",
                "enum": ["Ledger", "Voucher", "StockItem", "Company", "CostCentre"],
                "description": "The standard Tally master or transaction object configuration."
            },
            "tally_version": {
                "type": "string",
                "default": "Prime 4.0+",
                "description": "The release baseline for checking schema updates."
            }
        },
        "required": ["request_action", "object_type"]
    }
}

TALLY_COLLECTION_METADATA_TOOL = {
    "name": "query_tally_collection_metadata",
    "description": "Retrieve built-in Tally object schemas, standard extraction collection names, and internal attribute paths required to build data visibility pipelines.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "collection_name": {
                "type": "string",
                "description": "The exact name of the internal Tally collection (e.g., 'AllLedgers', 'VouchersOfType', 'StockStatus')."
            },
            "include_child_tables": {
                "type": "boolean",
                "default": True,
                "description": "Set to true to pull underlying repeating structures like inventory entries or tax breakdowns."
            }
        },
        "required": ["collection_name"]
    }
}

TALLY_GST_PATTERN_TOOL = {
    "name": "search_tally_gst_patterns",
    "description": "Query localized regulatory documentation specifically addressing Tally Prime data mappings for GSTR compliance, E-Way bills, and real-time E-Invoicing parameters.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "compliance_target": {
                "type": "string",
                "enum": ["GSTR-1_Mapping", "E-Way_Bill_JSON", "E-Invoicing_Payload", "TCS_TDS_Vouchers"],
                "description": "The specific Indian tax structure or logistics protocol to check documentation for."
            },
            "extraction_method": {
                "type": "string",
                "enum": ["ODBC_Query", "XML_Request_Direct", "TDL_Report_Custom"],
                "description": "The data ingestion path chosen by the system architecture."
            }
        },
        "required": ["compliance_target", "extraction_method"]
    }
}

TDL_SCAFFOLDING_TOOL = {
    "name": "get_tdl_extension_syntax",
    "description": "Fetch code patterns and structural syntax rules for Tally Definition Language (TDL) to construct temporary data views or extract user-defined fields (UDFs).",
    "inputSchema": {
        "type": "object",
        "properties": {
            "extension_type": {
                "type": "string",
                "enum": ["Custom_UDF_Extraction", "Report_Modification", "Collection_Filter"],
                "description": "The technical design objective of the generated TDL snippet."
            },
            "target_base_report": {
                "type": "string",
                "description": "The baseline Tally interface being extended (e.g., 'DayBook', 'TrialBalance', 'StockSummary')."
            }
        },
        "required": ["extension_type", "target_base_report"]
    }
}

ERP_INTEGRATION_TOOLS = [
    TALLY_XML_SCHEMA_ENGINE_TOOL,
    TALLY_COLLECTION_METADATA_TOOL,
    TALLY_GST_PATTERN_TOOL,
    TDL_SCAFFOLDING_TOOL
]
