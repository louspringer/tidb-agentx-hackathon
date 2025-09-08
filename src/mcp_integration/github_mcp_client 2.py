#!/usr/bin/env python3
"""
GitHub MCP Client - Integration with mcp-git-ingest
Provides intelligent repository context and file discovery
"""

import asyncio
import json
import logging
from typing import Any

from src.secure_shell_service.elegant_client import secure_execute


class GitHubMCPClient:
    """GitHub MCP Client for intelligent repository analysis"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mcp_server_path = None
        self._setup_mcp_server()

    def _setup_mcp_server(self):
        """Setup the MCP server connection"""
        try:
            # Check if mcp-git-ingest is available
            result = asyncio.run(secure_execute("which mcp-git-ingest"))
            if result["success"] and result["output"].strip():
                self.mcp_server_path = result["output"].strip()
                self.logger.info(f"✅ Found MCP server at: {self.mcp_server_path}")
            else:
                self.logger.warning(
                    "⚠️ mcp-git-ingest not found, will use fallback methods",
                )
        except Exception as e:
            self.logger.error(f"❌ Failed to setup MCP server: {e}")

    async def get_repository_structure(self, repo_url: str) -> str:
        """Get repository directory structure using MCP"""
        try:
            if self.mcp_server_path:
                # Use MCP server for intelligent structure analysis
                result = await secure_execute(
                    f"{self.mcp_server_path} directory-structure {repo_url}",
                )
                if result["success"]:
                    return result["output"]

            # Fallback: basic git clone and tree analysis
            return await self._fallback_repository_structure(repo_url)

        except Exception as e:
            self.logger.error(f"❌ Failed to get repository structure: {e}")
            return f"Error: {str(e)}"

    async def read_important_files(
        self,
        repo_url: str,
        file_paths: list[str],
    ) -> dict[str, str]:
        """Read important files using MCP"""
        try:
            if self.mcp_server_path:
                # Use MCP server for intelligent file reading
                file_paths_str = " ".join(file_paths)
                result = await secure_execute(
                    f"{self.mcp_server_path} read-files {repo_url} {file_paths_str}",
                )
                if result["success"]:
                    return json.loads(result["output"])

            # Fallback: basic file reading
            return await self._fallback_read_files(repo_url, file_paths)

        except Exception as e:
            self.logger.error(f"❌ Failed to read important files: {e}")
            return {"error": str(e)}

    async def analyze_repository(self, repo_url: str) -> dict[str, Any]:
        """Comprehensive repository analysis using MCP"""
        try:
            analysis = {
                "repo_url": repo_url,
                "structure": "",
                "important_files": {},
                "analysis": {},
            }

            # Get repository structure
            analysis["structure"] = await self.get_repository_structure(repo_url)

            # Identify and read important files
            important_files = [
                "README.md",
                "README.rst",
                "README.txt",
                "pyproject.toml",
                "setup.py",
                "requirements.txt",
                "package.json",
                "Cargo.toml",
                "go.mod",
                ".gitignore",
                "LICENSE",
                "CHANGELOG.md",
            ]

            analysis["important_files"] = await self.read_important_files(
                repo_url,
                important_files,
            )

            # Analyze the repository
            analysis["analysis"] = await self._analyze_repository_content(analysis)

            return analysis

        except Exception as e:
            self.logger.error(f"❌ Failed to analyze repository: {e}")
            return {"error": str(e)}

    async def _fallback_repository_structure(self, repo_url: str) -> str:
        """Fallback method for repository structure analysis"""
        try:
            # Clone repository temporarily
            temp_dir = f"/tmp/repo_analysis_{hash(repo_url) % 10000}"

            # Clone the repository
            clone_result = await secure_execute(f"git clone {repo_url} {temp_dir}")
            if not clone_result["success"]:
                return f"Error cloning repository: {clone_result['error']}"

            # Get directory structure
            tree_result = await secure_execute(
                f"find {temp_dir} -type f -name '.*' -prune -o -print | head -50",
            )

            # Cleanup
            await secure_execute(f"rm -rf {temp_dir}")

            if tree_result["success"]:
                return tree_result["output"]
            else:
                return f"Error getting structure: {tree_result['error']}"

        except Exception as e:
            return f"Fallback error: {str(e)}"

    async def _fallback_read_files(
        self,
        repo_url: str,
        file_paths: list[str],
    ) -> dict[str, str]:
        """Fallback method for reading files"""
        try:
            temp_dir = f"/tmp/repo_files_{hash(repo_url) % 10000}"

            # Clone repository
            clone_result = await secure_execute(f"git clone {repo_url} {temp_dir}")
            if not clone_result["success"]:
                return {"error": f"Failed to clone: {clone_result['error']}"}

            results = {}
            for file_path in file_paths:
                full_path = f"{temp_dir}/{file_path}"
                read_result = await secure_execute(
                    f"cat {full_path} 2>/dev/null || echo 'File not found'",
                )
                results[file_path] = (
                    read_result["output"]
                    if read_result["success"]
                    else "Error reading file"
                )

            # Cleanup
            await secure_execute(f"rm -rf {temp_dir}")

            return results

        except Exception as e:
            return {"error": f"Fallback error: {str(e)}"}

    async def _analyze_repository_content(
        self,
        analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """Analyze repository content and provide insights"""
        insights = {
            "project_type": "unknown",
            "languages": [],
            "dependencies": [],
            "key_files": [],
            "structure_quality": "unknown",
        }

        try:
            # Analyze structure
            structure = analysis.get("structure", "")
            if structure:
                # Count files by type
                file_extensions = []
                for line in structure.split("\n"):
                    if "." in line:
                        ext = line.split(".")[-1].split()[0]
                        if ext and len(ext) <= 5:
                            file_extensions.append(ext)

                # Determine project type
                if any(ext in ["py", "pyc"] for ext in file_extensions):
                    insights["project_type"] = "python"
                elif any(ext in ["js", "ts", "json"] for ext in file_extensions):
                    insights["project_type"] = "javascript"
                elif any(ext in ["go", "mod"] for ext in file_extensions):
                    insights["project_type"] = "go"
                elif any(ext in ["rs", "toml"] for ext in file_extensions):
                    insights["project_type"] = "rust"

                insights["languages"] = list(set(file_extensions))

            # Analyze important files
            important_files = analysis.get("important_files", {})

            if "pyproject.toml" in important_files:
                insights["dependencies"].append("Python (pyproject.toml)")
            if "package.json" in important_files:
                insights["dependencies"].append("Node.js (package.json)")
            if "go.mod" in important_files:
                insights["dependencies"].append("Go (go.mod)")
            if "Cargo.toml" in important_files:
                insights["dependencies"].append("Rust (Cargo.toml)")

            # Identify key files
            for file_name, content in important_files.items():
                if content and not content.startswith("Error"):
                    insights["key_files"].append(file_name)

            # Assess structure quality
            if len(insights["key_files"]) >= 3:
                insights["structure_quality"] = "good"
            elif len(insights["key_files"]) >= 1:
                insights["structure_quality"] = "basic"
            else:
                insights["structure_quality"] = "poor"

        except Exception as e:
            insights["error"] = str(e)

        return insights


# Convenience function for quick repository analysis
async def analyze_github_repository(repo_url: str) -> dict[str, Any]:
    """Quick repository analysis using GitHub MCP"""
    client = GitHubMCPClient()
    return await client.analyze_repository(repo_url)


# Example usage
async def main():
    """Example usage of GitHub MCP Client"""
    print("🔍 GitHub MCP Client - Intelligent Repository Analysis")
    print("=" * 60)

    # Test with our own repository
    repo_url = "https://github.com/louspringer/OpenFlow-Playground"

    client = GitHubMCPClient()
    analysis = await client.analyze_repository(repo_url)

    print("📊 Repository Analysis Results:")
    print(f"   URL: {analysis['repo_url']}")
    print(f"   Project Type: {analysis['analysis'].get('project_type', 'unknown')}")
    print(f"   Languages: {analysis['analysis'].get('languages', [])}")
    print(f"   Dependencies: {analysis['analysis'].get('dependencies', [])}")
    print(f"   Key Files: {analysis['analysis'].get('key_files', [])}")
    print(
        f"   Structure Quality: {analysis['analysis'].get('structure_quality', 'unknown')}",
    )

    print("\n📁 Repository Structure (first 200 chars):")
    structure = analysis.get("structure", "No structure available")
    print(structure[:200] + "..." if len(structure) > 200 else structure)


if __name__ == "__main__":
    asyncio.run(main())
