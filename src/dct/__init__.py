"""defunct-company-tracker (dct).

Generate a source-cited, fact-verified static website tracking whether companies
are active, acquired, or defunct — researched by an internet-capable LLM, with a
verification layer that refuses to publish unsourced claims.
"""

from .models import Citation, Company, Status, StatusReport
from .pipeline import PipelineResult, load_companies, parse_companies, run_pipeline
from .providers import (
    AnthropicProvider,
    MockProvider,
    default_provider,
    parse_model_payload,
)
from .verify import VerifyConfig, verify_report
from .cache import ReportCache
from .site import SiteGenerator

__version__ = "0.1.0"

__all__ = [
    "Citation",
    "Company",
    "Status",
    "StatusReport",
    "PipelineResult",
    "load_companies",
    "parse_companies",
    "run_pipeline",
    "AnthropicProvider",
    "MockProvider",
    "default_provider",
    "parse_model_payload",
    "VerifyConfig",
    "verify_report",
    "ReportCache",
    "SiteGenerator",
    "__version__",
]
