#!/usr/bin/env python3
"""
MCP Expert Agent for Ghostbusters
Handles Model Context Protocol integration and analysis
"""

from pathlib import Path

from .base_expert import BaseExpert, DelusionResult


class MCPExpert(BaseExpert):
    """Expert agent for MCP (Model Context Protocol) analysis"""

    def __init__(self) -> None:
        super().__init__("MCPExpert")
        self.description = "Analyzes Model Context Protocol integration and usage"

    async def detect_delusions(self, project_path: Path) -> DelusionResult:
        """Detect MCP-related delusions in the project"""
        delusions = []
        recommendations = []

        try:
            # Check for MCP configuration files
            mcp_files = list(project_path.rglob("*.mcp"))
            mcp_config_files = list(project_path.rglob("mcp*.json"))
            mcp_config_files.extend(list(project_path.rglob("mcp*.yaml")))
            mcp_config_files.extend(list(project_path.rglob("mcp*.yml")))

            # Check for MCP integration code
            mcp_integration_files = []
            for pattern in ["*mcp*", "*model_context*", "*protocol*"]:
                mcp_integration_files.extend(project_path.rglob(pattern))

            # Analyze MCP usage
            if not mcp_files and not mcp_config_files:
                delusions.append(
                    self._create_delusion(
                        "missing_mcp_config",
                        str(project_path),
                        0,
                        "No MCP configuration files found",
                        0.7,
                        "low",
                    ),
                )

            # Check for proper MCP client implementation
            mcp_client_files = list(project_path.rglob("*mcp_client*"))
            if not mcp_client_files:
                delusions.append(
                    self._create_delusion(
                        "missing_mcp_client",
                        str(project_path),
                        0,
                        "No MCP client implementation found",
                        0.8,
                        "medium",
                    ),
                )

            # Check for MCP server implementation
            mcp_server_files = list(project_path.rglob("*mcp_server*"))
            if not mcp_server_files:
                delusions.append(
                    self._create_delusion(
                        "missing_mcp_server",
                        str(project_path),
                        0,
                        "No MCP server implementation found",
                        0.8,
                        "medium",
                    ),
                )

        except Exception as e:
            delusions.append(
                self._create_delusion(
                    "mcp_analysis_error",
                    str(project_path),
                    0,
                    f"Error analyzing MCP integration: {e}",
                    0.9,
                    "high",
                ),
            )

        # Generate recommendations
        if delusions:
            for delusion in delusions:
                if delusion["type"] == "missing_mcp_config":
                    recommendations.append(
                        self._create_recommendation(
                            "Create MCP configuration file with proper model context settings",
                            "low",
                        ),
                    )
                elif delusion["type"] == "missing_mcp_client":
                    recommendations.append(
                        self._create_recommendation(
                            "Implement MCP client for connecting to model context servers",
                            "medium",
                        ),
                    )
                elif delusion["type"] == "missing_mcp_server":
                    recommendations.append(
                        self._create_recommendation(
                            "Implement MCP server for providing model context services",
                            "medium",
                        ),
                    )
        else:
            recommendations.append(
                self._create_recommendation(
                    "MCP integration looks good",
                    "low",
                ),
            )

        confidence = self._calculate_confidence(delusions)

        return DelusionResult(
            delusions=delusions,
            confidence=confidence,
            recommendations=recommendations,
            agent_name=self.name,
        )
