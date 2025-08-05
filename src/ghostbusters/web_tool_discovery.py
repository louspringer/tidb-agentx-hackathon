#!/usr/bin/env python3
"""
Web Tool Discovery - Find existing tools in the ecosystem
"""

from typing import Any

import requests


class WebToolDiscovery:
    """Discover tools from web search and GitHub"""

    def __init__(self) -> None:
        self.github_api_base = "https://api.github.com"
        self.pypi_api_base = "https://pypi.org/pypi"

    def search_github_tools(self, issue_type: str) -> list[dict[str, Any]]:
        """Search GitHub for tools that solve specific issues"""

        # Map issue types to search terms
        search_terms = {
            "mypy_return_value": ["mypy return value fix", "python type checker fix"],
            "flake8_style": ["flake8 auto fix", "python style auto fix"],
            "syntax_error": ["python syntax fix", "ast parser fix"],
            "unused_imports": ["remove unused imports", "python import cleaner"],
            "f_strings": ["f-string fix", "python string formatting"],
            "subprocess_vulnerability": [
                "python subprocess security",
                "command injection prevention",
                "secure shell execution",
            ],
            "shell_security": [
                "gRPC shell service",
                "secure command execution",
                "Go shell operations",
            ],
            "performance_hanging": [
                "python subprocess timeout",
                "hanging process detection",
                "resource monitoring",
            ],
        }

        tools_found = []

        for search_term in search_terms.get(issue_type, [issue_type]):
            try:
                # Search GitHub repositories
                url = f"{self.github_api_base}/search/repositories"
                params = {
                    "q": f"{search_term} language:python",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 5,
                }

                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for repo in data.get("items", []):
                        tools_found.append(
                            {
                                "name": repo["name"],
                                "full_name": repo["full_name"],
                                "description": repo["description"],
                                "stars": repo["stargazers_count"],
                                "url": repo["html_url"],
                                "type": "github_repo",
                                "search_term": search_term,
                            },
                        )

            except Exception as e:
                print(f"❌ GitHub search failed for {search_term}: {e}")

        return tools_found

    def search_pypi_tools(self, issue_type: str) -> list[dict[str, Any]]:
        """Search PyPI for packages that solve specific issues"""

        # Map issue types to PyPI search terms
        pypi_terms = {
            "mypy_return_value": ["mypy", "type-checker", "type-fix"],
            "flake8_style": ["flake8", "style-checker", "auto-fix"],
            "syntax_error": ["ast", "syntax", "parser"],
            "unused_imports": ["import", "cleaner", "unused"],
            "f_strings": ["string", "format", "f-string"],
            "subprocess_vulnerability": ["subprocess", "security", "command-execution"],
            "shell_security": ["grpc", "shell", "secure-execution"],
            "performance_hanging": [
                "timeout",
                "resource-monitoring",
                "process-management",
            ],
        }

        tools_found = []

        for search_term in pypi_terms.get(issue_type, [issue_type]):
            try:
                # Search PyPI
                url = "https://pypi.org/search/"
                params = {"q": search_term, "o": "-created"}

                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    # Parse PyPI search results (simplified)
                    if search_term in response.text:
                        tools_found.append(
                            {
                                "name": f"pypi-{search_term}",
                                "type": "pypi_package",
                                "search_term": search_term,
                                "url": f"https://pypi.org/project/{search_term}/",
                            },
                        )

            except Exception as e:
                print(f"❌ PyPI search failed for {search_term}: {e}")

        return tools_found

    def get_web_recommendations(self, analysis_results: dict[str, Any]) -> list[str]:
        """Get web-based recommendations for issues"""
        recommendations = []

        # Check what issues we have
        mypy_errors = analysis_results.get("mypy", {}).get("total_errors", 0)
        flake8_errors = analysis_results.get("flake8", {}).get("total_errors", 0)
        ast_errors = analysis_results.get("ast", {}).get("total_errors", 0)
        subprocess_vulnerabilities = analysis_results.get(
            "subprocess_vulnerability",
            {},
        ).get("total_errors", 0)
        shell_security_issues = analysis_results.get("shell_security", {}).get(
            "total_errors",
            0,
        )

        # Search for tools based on issues
        if mypy_errors > 0:
            github_tools = self.search_github_tools("mypy_return_value")
            pypi_tools = self.search_pypi_tools("mypy_return_value")

            if github_tools:
                top_tool = github_tools[0]
                recommendations.append(
                    f"Found GitHub tool: {top_tool['name']} ({top_tool['stars']} stars) - {top_tool['description']}",
                )

            if pypi_tools:
                recommendations.append(
                    f"Found PyPI package: {pypi_tools[0]['name']} for MyPy issues",
                )

        if flake8_errors > 0:
            github_tools = self.search_github_tools("flake8_style")
            pypi_tools = self.search_pypi_tools("flake8_style")

            if github_tools:
                top_tool = github_tools[0]
                recommendations.append(
                    f"Found GitHub tool: {top_tool['name']} ({top_tool['stars']} stars) - {top_tool['description']}",
                )

            if pypi_tools:
                recommendations.append(
                    f"Found PyPI package: {pypi_tools[0]['name']} for Flake8 issues",
                )

        if ast_errors > 0:
            github_tools = self.search_github_tools("syntax_error")
            pypi_tools = self.search_pypi_tools("syntax_error")

            if github_tools:
                top_tool = github_tools[0]
                recommendations.append(
                    f"Found GitHub tool: {top_tool['name']} ({top_tool['stars']} stars) - {top_tool['description']}",
                )

        # Check for subprocess security vulnerabilities
        if subprocess_vulnerabilities > 0:
            github_tools = self.search_github_tools("subprocess_vulnerability")
            pypi_tools = self.search_pypi_tools("subprocess_vulnerability")

            if github_tools:
                top_tool = github_tools[0]
                recommendations.append(
                    f"Found GitHub tool: {top_tool['name']} ({top_tool['stars']} stars) - {top_tool['description']}",
                )

            if pypi_tools:
                recommendations.append(
                    f"Found PyPI package: {pypi_tools[0]['name']} for subprocess security",
                )

        # Check for shell security issues
        if shell_security_issues > 0:
            github_tools = self.search_github_tools("shell_security")
            pypi_tools = self.search_pypi_tools("shell_security")

            if github_tools:
                top_tool = github_tools[0]
                recommendations.append(
                    f"Found GitHub tool: {top_tool['name']} ({top_tool['stars']} stars) - {top_tool['description']}",
                )

        if not recommendations:
            recommendations.append(
                "No existing tools found in web search - manual fixes required",
            )

        return recommendations


if __name__ == "__main__":
    web_discovery = WebToolDiscovery()

    # Test with sample analysis results
    sample_results = {
        "mypy": {"total_errors": 1},
        "flake8": {"total_errors": 198},
        "ast": {"total_errors": 9},
    }

    recommendations = web_discovery.get_web_recommendations(sample_results)

    print("🔍 Web Tool Discovery Results:")
    for rec in recommendations:
        print(f"   • {rec}")
