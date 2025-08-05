#!/usr/bin/env python3
"""
Live Progress Updater for AST Level Up Process
Updates live_progress_data.json with real-time progress
"""

import json
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, Any


class ProgressUpdater:
    """Updates live progress data for the HTML pacifier"""
    
    def __init__(self, data_file: str = "live_progress_data.json"):
        self.data_file = data_file
        self.data = self.load_data()
    
    def load_data(self) -> Dict[str, Any]:
        """Load existing progress data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Default data
        return {
            "total_files": 84,
            "fixed_files": 54,
            "broken_files": 30,
            "checkpoints": 2,
            "current_file": "",
            "current_hypothesis": "",
            "current_action": "",
            "validation_results": {
                "syntax": "pending",
                "linter": "pending",
                "mypy": "pending"
            },
            "recent_activity": [],
            "last_updated": datetime.now().strftime("%H:%M:%S")
        }
    
    def save_data(self) -> None:
        """Save progress data to JSON file"""
        self.data["last_updated"] = datetime.now().strftime("%H:%M:%S")
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def update_current_file(self, filename: str, hypothesis: str, action: str) -> None:
        """Update current file being worked on"""
        self.data["current_file"] = filename
        self.data["current_hypothesis"] = hypothesis
        self.data["current_action"] = action
        # Add the "Working on..." message for tracking
        self.add_activity(f"Working on {filename} - {action}")
        self.save_data()
    
    def update_validation_results(self, results: Dict[str, str]) -> None:
        """Update validation results"""
        self.data["validation_results"].update(results)
        self.save_data()
    
    def file_fixed(self, filename: str) -> None:
        """Mark a file as fixed"""
        self.data["fixed_files"] += 1
        self.data["broken_files"] = max(0, self.data["broken_files"] - 1)
        # Add the "Fixed..." message for tracking
        self.add_activity(f"✅ Fixed {filename} - syntax and linter issues resolved")
        self.save_data()
    
    def file_failed(self, filename: str, error: str) -> None:
        """Mark a file as failed"""
        self.add_activity(f"❌ Failed to fix {filename} - {error}")
        self.save_data()
    
    def add_activity(self, message: str) -> None:
        """Add activity to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.data["recent_activity"].append({
            "timestamp": timestamp,
            "message": message
        })
        
        # Keep only last 10 activities
        if len(self.data["recent_activity"]) > 10:
            self.data["recent_activity"] = self.data["recent_activity"][-10:]
        
        self.save_data()
    
    def update_checkpoints(self, count: int) -> None:
        """Update checkpoint count"""
        self.data["checkpoints"] = count
        self.save_data()


def main() -> None:
    """Handle command-line arguments and update progress"""
    parser = argparse.ArgumentParser(description="Update AST Level Up progress")
    parser.add_argument("--update-file", nargs=3, metavar=("FILE", "HYPOTHESIS", "ACTION"),
                       help="Update current file with hypothesis and action")
    parser.add_argument("--file-fixed", metavar="FILE", help="Mark file as fixed")
    parser.add_argument("--file-failed", nargs=2, metavar=("FILE", "ERROR"),
                       help="Mark file as failed with error")
    parser.add_argument("--add-activity", metavar="MESSAGE", help="Add activity message")
    parser.add_argument("--update-validation", nargs=2, metavar=("TYPE", "STATUS"),
                       help="Update validation result (syntax/linter/mypy)")
    parser.add_argument("--update-checkpoints", type=int, metavar="COUNT",
                       help="Update checkpoint count")
    
    args = parser.parse_args()
    updater = ProgressUpdater()
    
    if args.update_file:
        filename, hypothesis, action = args.update_file
        updater.update_current_file(filename, hypothesis, action)
        print(f"Updated current file: {filename}")
    
    elif args.file_fixed:
        updater.file_fixed(args.file_fixed)
        print(f"Marked as fixed: {args.file_fixed}")
    
    elif args.file_failed:
        filename, error = args.file_failed
        updater.file_failed(filename, error)
        print(f"Marked as failed: {filename}")
    
    elif args.add_activity:
        updater.add_activity(args.add_activity)
        print(f"Added activity: {args.add_activity}")
    
    elif args.update_validation:
        validation_type, status = args.update_validation
        updater.update_validation_results({validation_type: status})
        print(f"Updated validation {validation_type}: {status}")
    
    elif args.update_checkpoints:
        updater.update_checkpoints(args.update_checkpoints)
        print(f"Updated checkpoints: {args.update_checkpoints}")
    
    else:
        # Default test behavior
        updater.update_current_file(
            "tests/test_cline_plan_blind_spots.py",
            "File has severe indentation issues requiring complete rewrite",
            "Complete rewrite due to broken indentation structure"
        )
        print("✅ Progress data updated!")


if __name__ == "__main__":
    main() 