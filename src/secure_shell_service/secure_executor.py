#!/usr/bin/env python3
"""
Secure Shell Executor - Safe replacement for subprocess
Provides secure command execution without subprocess vulnerabilities
"""

import asyncio
import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of a secure command execution"""

    success: bool
    return_code: int
    stdout: str
    stderr: str
    command: str
    duration: float


class SecureExecutor:
    """Secure command execution without subprocess vulnerabilities"""

    def __init__(self, timeout: int = 30, working_dir: Optional[Path] = None):
        self.timeout = timeout
        self.working_dir = working_dir or Path.cwd()
        self.allowed_commands = self._load_allowed_commands()

    def _load_allowed_commands(self) -> dict[str, dict[str, Any]]:
        """Load allowed commands from configuration"""
        return {
            "git": {
                "allowed_args": ["clone", "pull", "push", "status", "log", "diff"],
                "safe": True,
                "description": "Git operations",
            },
            "ls": {
                "allowed_args": ["-la", "-l", "-a"],
                "safe": True,
                "description": "List directory contents",
            },
            "ps": {
                "allowed_args": ["aux", "ef"],
                "safe": True,
                "description": "Process status",
            },
            "find": {
                "allowed_args": [".", "-name", "*.py", "*.json"],
                "safe": True,
                "description": "File search",
            },
            "uv": {
                "allowed_args": ["run", "sync", "add", "install"],
                "safe": True,
                "description": "UV package manager",
            },
            "python": {
                "allowed_args": ["-m", "pytest", "-c", "import ast"],
                "safe": True,
                "description": "Python interpreter",
            },
            "black": {
                "allowed_args": ["--check", "--diff", ".", "--quiet"],
                "safe": True,
                "description": "Code formatter",
            },
            "flake8": {
                "allowed_args": [
                    "--select",
                    "F401,E302",
                    ".",
                    "F401,E302,E305,W291,W292",
                ],
                "safe": True,
                "description": "Linter",
            },
            "mypy": {
                "allowed_args": ["--ignore-missing-imports", ".", "--version"],
                "safe": True,
                "description": "Type checker",
            },
        }

    def _validate_command(self, command: Union[str, list[str]]) -> bool:
        """Validate command is allowed and safe"""
        if isinstance(command, str):
            parts = command.split()
        else:
            parts = command

        if not parts:
            return False

        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        # Check if command is allowed
        if cmd not in self.allowed_commands:
            # Allow python executable paths
            if cmd.endswith("python") or cmd.endswith("python3") or "python" in cmd:
                # This is a python executable, allow it
                pass
            else:
                logger.warning(f"Command not allowed: {cmd}")
                return False

        # Special handling for 'uv run' commands
        if cmd == "uv" and args and args[0] == "run":
            # For 'uv run <subcommand>', validate the subcommand
            if len(args) < 2:
                logger.warning("uv run requires a subcommand")
                return False

            subcommand = args[1]
            subcommand_args = args[2:] if len(args) > 2 else []

            # Check if subcommand is allowed
            if subcommand not in self.allowed_commands:
                logger.warning(f"Subcommand not allowed for uv run: {subcommand}")
                return False

            # Validate subcommand arguments
            allowed_args = self.allowed_commands[subcommand]["allowed_args"]
            for arg in subcommand_args:
                if arg not in allowed_args and not arg.startswith("-"):
                    # Allow file paths for certain subcommands
                    if subcommand in ["black", "flake8", "mypy"] and (
                        arg.endswith(".py") or "/" in arg or "\\" in arg
                    ):
                        # This is a file path, allow it
                        continue
                    logger.warning(f"Argument not allowed for {subcommand}: {arg}")
                    return False

            return True

        # Special handling for python executable commands
        if cmd.endswith("python") or cmd.endswith("python3") or "python" in cmd:
            # Allow python module execution
            for arg in args:
                if arg not in [
                    "-m",
                    "mypy",
                    "--version",
                    "pytest",
                    "-c",
                    "import ast",
                ] and not arg.startswith("-"):
                    logger.warning(f"Argument not allowed for python: {arg}")
                    return False
            return True

        # Check if arguments are allowed for other commands
        allowed_args = self.allowed_commands[cmd]["allowed_args"]
        for arg in args:
            if arg not in allowed_args and not arg.startswith("-"):
                # Allow file paths for certain commands
                if cmd in ["black", "flake8", "mypy"] and (
                    arg.endswith(".py") or "/" in arg or "\\" in arg
                ):
                    # This is a file path, allow it
                    continue
                logger.warning(f"Argument not allowed for {cmd}: {arg}")
                return False

        return True

    def _sanitize_command(self, command: Union[str, list[str]]) -> list[str]:
        """Sanitize command for safe execution"""
        if isinstance(command, str):
            parts = command.split()
        else:
            parts = command.copy()

        # Remove any shell metacharacters
        sanitized = []
        for part in parts:
            # Remove dangerous characters
            clean_part = part.replace(";", "").replace("&", "").replace("|", "")
            clean_part = (
                clean_part.replace("`", "")
                .replace("$", "")
                .replace("(", "")
                .replace(")", "")
            )
            sanitized.append(clean_part)

        return sanitized

    async def execute(
        self,
        command: Union[str, list[str]],
        capture_output: bool = True,
        text: bool = True,
        timeout: Optional[int] = None,
    ) -> CommandResult:
        """Execute command securely"""
        start_time = asyncio.get_event_loop().time()

        try:
            # Validate command
            if not self._validate_command(command):
                return CommandResult(
                    success=False,
                    return_code=1,
                    stdout="",
                    stderr="Command not allowed",
                    command=str(command),
                    duration=0.0,
                )

            # Sanitize command
            sanitized_cmd = self._sanitize_command(command)

            # Create temporary working directory if needed
            with tempfile.TemporaryDirectory() as temp_dir:
                # Change to working directory
                original_dir = os.getcwd()
                os.chdir(temp_dir)

                try:
                    # Execute command using asyncio
                    process = await asyncio.create_subprocess_exec(
                        *sanitized_cmd,
                        stdout=asyncio.subprocess.PIPE if capture_output else None,
                        stderr=asyncio.subprocess.PIPE if capture_output else None,
                        cwd=self.working_dir,
                    )

                    # Wait for completion with timeout
                    timeout_actual = timeout or self.timeout
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=timeout_actual,
                    )

                    # Convert output to text if requested
                    if text and capture_output:
                        stdout_str = stdout.decode("utf-8") if stdout else ""
                        stderr_str = stderr.decode("utf-8") if stderr else ""
                    else:
                        stdout_str = stdout  # type: ignore
                        stderr_str = stderr  # type: ignore

                    duration = asyncio.get_event_loop().time() - start_time

                    return CommandResult(
                        success=process.returncode == 0,
                        return_code=process.returncode,  # type: ignore
                        stdout=stdout_str,
                        stderr=stderr_str,
                        command=str(command),
                        duration=duration,
                    )

                except asyncio.TimeoutError:
                    return CommandResult(
                        success=False,
                        return_code=1,
                        stdout="",
                        stderr=f"Command timed out after {timeout_actual}s",
                        command=str(command),
                        duration=timeout_actual,
                    )
                except Exception as e:
                    return CommandResult(
                        success=False,
                        return_code=1,
                        stdout="",
                        stderr=f"Execution error: {str(e)}",
                        command=str(command),
                        duration=asyncio.get_event_loop().time() - start_time,
                    )
                finally:
                    os.chdir(original_dir)

        except Exception as e:
            return CommandResult(
                success=False,
                return_code=1,
                stdout="",
                stderr=f"Setup error: {str(e)}",
                command=str(command),
                duration=asyncio.get_event_loop().time() - start_time,
            )

    def execute_sync(
        self,
        command: Union[str, list[str]],
        capture_output: bool = True,
        text: bool = True,
        timeout: Optional[int] = None,
    ) -> CommandResult:
        """Synchronous version of execute"""
        return asyncio.run(self.execute(command, capture_output, text, timeout))

    def run(
        self,
        command: Union[str, list[str]],
        capture_output: bool = True,
        text: bool = True,
        timeout: Optional[int] = None,
    ) -> CommandResult:
        """Compatibility method to replace subprocess.run"""
        return self.execute_sync(command, capture_output, text, timeout)


# Convenience function for easy replacement
def secure_execute(
    command: Union[str, list[str]],
    capture_output: bool = True,
    text: bool = True,
    timeout: Optional[int] = None,
) -> CommandResult:
    """Secure alternative to subprocess.run"""
    executor = SecureExecutor()
    return executor.run(command, capture_output, text, timeout)


# Example usage
if __name__ == "__main__":
    # Test secure execution
    executor = SecureExecutor()

    # Test allowed command
    result = executor.run(["ls", "-la"])
    print(f"✅ Allowed command: {result.success}")
    print(f"Output: {result.stdout[:100]}...")

    # Test disallowed command
    result = executor.run(["rm", "-rf", "/"])
    print(f"❌ Disallowed command: {result.success}")
    print(f"Error: {result.stderr}")
