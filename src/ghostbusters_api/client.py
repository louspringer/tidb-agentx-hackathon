#!/usr/bin/env python3
"""
Ghostbusters API Client
Python client for the proper Ghostbusters API service
"""

import time
from typing import Any

import requests


class GhostbustersAPIClient:
    """Client for the Ghostbusters API service"""

    def __init__(
        self,
        base_url: str = "https://us-central1-aardvark-linkedin-grepper.cloudfunctions.net",
    ):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "GhostbustersAPIClient/1.0",
            },
        )

    def analyze_project(
        self,
        project_path: str = ".",
        agents: list[str] = None,
    ) -> dict[str, Any]:
        """Queue a Ghostbusters analysis job"""
        if agents is None:
            agents = ["security", "code_quality"]

        payload = {"project_path": project_path, "agents": agents}

        response = self.session.post(
            f"{self.base_url}/ghostbusters-analyze",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def recover_project(
        self,
        recovery_type: str,
        target_files: list[str] = None,
        project_path: str = ".",
    ) -> dict[str, Any]:
        """Queue a Ghostbusters recovery job"""
        if target_files is None:
            target_files = []

        payload = {
            "recovery_type": recovery_type,
            "target_files": target_files,
            "project_path": project_path,
        }

        response = self.session.post(
            f"{self.base_url}/ghostbusters-recover",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def get_job_status(self, job_id: str) -> dict[str, Any]:
        """Get the status of a Ghostbusters job"""
        response = self.session.get(
            f"{self.base_url}/ghostbusters-status",
            params={"job_id": job_id},
        )
        response.raise_for_status()
        return response.json()

    def list_jobs(self) -> dict[str, Any]:
        """List user's Ghostbusters jobs"""
        response = self.session.get(f"{self.base_url}/ghostbusters-jobs")
        response.raise_for_status()
        return response.json()

    def wait_for_completion(
        self,
        job_id: str,
        timeout: int = 300,
        poll_interval: int = 5,
    ) -> dict[str, Any]:
        """Wait for a job to complete and return the final result"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_job_status(job_id)

            if status.get("status") in ["completed", "failed"]:
                return status

            time.sleep(poll_interval)

        raise TimeoutError(f"Job {job_id} did not complete within {timeout} seconds")


def main():
    """Demo the Ghostbusters API client"""
    client = GhostbustersAPIClient()

    print("🎯 Ghostbusters API Client Demo")
    print("=" * 50)

    # Queue an analysis
    print("\n📊 Queuing analysis...")
    analysis_result = client.analyze_project(".", ["security", "code_quality"])
    job_id = analysis_result["job_id"]
    print(f"✅ Analysis queued: {job_id}")

    # Wait for completion
    print("\n⏳ Waiting for analysis to complete...")
    final_result = client.wait_for_completion(job_id)

    print("\n📋 Analysis Results:")
    print(f"  Status: {final_result['status']}")
    print(f"  Project: {final_result['project_path']}")
    print(f"  Agents: {final_result['agents']}")

    if final_result.get("result"):
        result = final_result["result"]
        print(f"  Delusions Found: {result.get('delusions_found', 0)}")
        print(f"  Analysis Time: {result.get('analysis_time', 'N/A')}")

        if result.get("delusions"):
            print("\n🔍 Delusions Found:")
            for delusion in result["delusions"]:
                print(
                    f"  - {delusion['type']}: {delusion['description']} ({delusion['severity']})",
                )

    # Queue a recovery
    print("\n🔧 Queuing recovery...")
    recovery_result = client.recover_project("syntax", ["src/main.py"])
    recovery_job_id = recovery_result["job_id"]
    print(f"✅ Recovery queued: {recovery_job_id}")

    # Wait for recovery completion
    print("\n⏳ Waiting for recovery to complete...")
    recovery_final = client.wait_for_completion(recovery_job_id)

    print("\n🔧 Recovery Results:")
    print(f"  Status: {recovery_final['status']}")
    print(f"  Recovery Type: {recovery_final['recovery_type']}")
    print(f"  Target Files: {recovery_final['target_files']}")

    if recovery_final.get("result"):
        result = recovery_final["result"]
        print(f"  Files Processed: {result.get('files_processed', 0)}")
        print(f"  Files Fixed: {result.get('files_fixed', 0)}")
        print(f"  Recovery Time: {result.get('recovery_time', 'N/A')}")

    print("\n🎉 Demo completed successfully!")


if __name__ == "__main__":
    main()
