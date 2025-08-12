"""
TiDB AgentX Hackathon 2025

AI-powered multi-agent testing with TiDB Serverless
$30,500 prize submission
"""

__version__ = "0.1.0"
__author__ = "Lou Springer"
__email__ = "lou@example.com"

from .agents import MultiAgentTestingService
from .core import TiDBAgentOrchestrator
from .tidb_integration import TiDBServerlessClient
from .workflows import RealWorldWorkflowEngine

__all__ = [
    "TiDBAgentOrchestrator",
    "MultiAgentTestingService",
    "TiDBServerlessClient",
    "RealWorldWorkflowEngine",
]
