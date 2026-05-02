"""
Mock data generation package for AI Packaging Reliability Copilot
"""

from .config_schema import (
    ProcessStage,
    Status,
    ParameterRange,
    ALL_PARAMETERS,
    CRITICAL_PARAMETERS,
    CROSS_STAGE_DEPENDENCIES,
    ISSUE_MAPPING,
    get_parameter_status,
    classify_overall_status,
    get_all_parameter_names,
    get_parameter_range,
)

__all__ = [
    "ProcessStage",
    "Status",
    "ParameterRange",
    "ALL_PARAMETERS",
    "CRITICAL_PARAMETERS",
    "CROSS_STAGE_DEPENDENCIES",
    "ISSUE_MAPPING",
    "get_parameter_status",
    "classify_overall_status",
    "get_all_parameter_names",
    "get_parameter_range",
]

# Made with Bob
