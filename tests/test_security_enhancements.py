#!/usr/bin/env python3
"""
Test Security Enhancements
Validates the security blind spot fixes implemented based on Gemini 2.5 Flash Lite recommendations.
"""

import json
import sys
from pathlib import Path

            return json.load(f)
    except FileNotFoundError:
        print("❌ project_model_registry.json not found")
        return None



