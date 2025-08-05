#!/usr/bin/env python3
"""
Ghostbusters Analytics Dashboard
Cloud Run application for visualizing analysis results
"""

import logging
from datetime import datetime, timedelta
from typing import Any

import streamlit as st
from firebase_admin import initialize_app
from google.cloud import firestore, pubsub_v1

# Initialize Firebase Admin SDK
try:
    initialize_app()
except ValueError:
    # App already initialized
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firestore client
db = firestore.Client()

# Initialize Pub/Sub subscriber for real-time updates
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(
    "ghostbusters-project",
    "analysis-updates-sub",
)

# Page configuration
st.set_page_config(
    page_title="Ghostbusters Analytics Dashboard",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-card {
        border-left-color: #28a745;
    }
    .warning-card {
        border-left-color: #ffc107;
    }
    .error-card {
        border-left-color: #dc3545;
    }
</style>
""",
    unsafe_allow_html=True,
)


def authenticate_user() -> str:
    """Authenticate user using Firebase Auth"""
    try:
        # In a real app, you'd get the token from the frontend
        # For demo purposes, we'll use a mock user
        return "demo-user-123"
    except Exception as e:
        logger.error("Authentication failed: %s", str(e))
        return None


def get_user_analyses(user_id: str, limit: int = 50) -> list[dict[str, Any]]:
    """Get user's analysis history"""
    try:
        docs = (
            db.collection("ghostbusters_results")
            .where("user_id", "==", user_id)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )

        analyses = []
        for doc in docs:
            data = doc.to_dict()
            analyses.append(
                {
                    "analysis_id": data.get("analysis_id"),
                    "project_path": data.get("project_path"),
                    "confidence_score": data.get("confidence_score", 0),
                    "delusions_detected": len(data.get("delusions_detected", [])),
                    "recovery_actions": len(data.get("recovery_actions", [])),
                    "errors": len(data.get("errors", [])),
                    "warnings": len(data.get("warnings", [])),
                    "processing_time": data.get("processing_time", 0),
                    "timestamp": data.get("timestamp"),
                    "status": data.get("status", "unknown"),
                    "agents_used": data.get("agents_used", []),
                },
            )

        return analyses
    except Exception as e:
        logger.error("Failed to get user analyses: %s", str(e))
        return []


def get_analysis_details(analysis_id: str) -> dict[str, Any]:
    """Get detailed analysis results"""
    try:
        doc = db.collection("ghostbusters_results").document(analysis_id).get()
        if doc.exists:
            return doc.to_dict()
        return {}
    except Exception as e:
        logger.error("Failed to get analysis details: %s", str(e))
        return {}


def get_global_metrics() -> dict[str, Any]:
    """Get global analytics metrics"""
    try:
        # Get total analyses
        total_analyses = len(list(db.collection("ghostbusters_results").stream()))

        # Get recent analyses (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_analyses = list(
            db.collection("ghostbusters_results")
            .where("timestamp", ">=", week_ago)
            .stream(),
        )

        # Calculate metrics
        total_delusions = sum(
            len(doc.to_dict().get("delusions_detected", [])) for doc in recent_analyses
        )
        total_recoveries = sum(
            len(doc.to_dict().get("recovery_actions", [])) for doc in recent_analyses
        )
        avg_confidence = (
            sum(doc.to_dict().get("confidence_score", 0) for doc in recent_analyses)
            / len(recent_analyses)
            if recent_analyses
            else 0
        )
        avg_processing_time = (
            sum(doc.to_dict().get("processing_time", 0) for doc in recent_analyses)
            / len(recent_analyses)
            if recent_analyses
            else 0
        )

        return {
            "total_analyses": total_analyses,
            "recent_analyses": len(recent_analyses),
            "total_delusions": total_delusions,
            "total_recoveries": total_recoveries,
            "avg_confidence": avg_confidence,
            "avg_processing_time": avg_processing_time,
        }
    except Exception as e:
        logger.error("Failed to get global metrics: %s", str(e))
        return {}


def main():
    """Main dashboard application"""

    # Header
    st.markdown(
        '<h1 class="main-header">👻 Ghostbusters Analytics Dashboard</h1>',
        unsafe_allow_html=True,
    )

    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        [
            "Overview",
            "My Analyses",
            "Analysis Details",
            "Real-time Updates",
            "Settings",
        ],
    )

    # Authenticate user
    user_id = authenticate_user()
    if not user_id:
        st.error("Authentication failed. Please log in.")
        return

    st.sidebar.success(f"Logged in as: {user_id}")

    if page == "Overview":
        show_overview(user_id)
    elif page == "My Analyses":
        show_my_analyses(user_id)
    elif page == "Analysis Details":
        show_analysis_details()
    elif page == "Real-time Updates":
        show_real_time_updates()
    elif page == "Settings":
        show_settings()


def show_overview(user_id: str):
    """Show overview dashboard"""
    st.header("📊 Overview")

    # Get metrics
    global_metrics = get_global_metrics()
    user_analyses = get_user_analyses(user_id, limit=10)

    # Global metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Analyses",
            global_metrics.get("total_analyses", 0),
            delta=global_metrics.get("recent_analyses", 0),
        )

    with col2:
        st.metric(
            "Avg Confidence",
            f"{global_metrics.get('avg_confidence', 0):.2f}",
            delta="+0.05",
        )

    with col3:
        st.metric(
            "Avg Processing Time",
            f"{global_metrics.get('avg_processing_time', 0):.1f}s",
            delta="-0.5s",
        )

    # Recent activity
    st.subheader("Recent Activity")
    if user_analyses:
        for analysis in user_analyses[:5]:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                with col1:
                    st.write(f"**{analysis['project_path']}**")
                    st.caption(f"Analysis ID: {analysis['analysis_id'][:8]}...")

                with col2:
                    confidence_color = (
                        "green"
                        if analysis["confidence_score"] > 0.8
                        else "orange"
                        if analysis["confidence_score"] > 0.6
                        else "red"
                    )
                    st.markdown(
                        f"<span style='color: {confidence_color}; font-weight: bold;'>{analysis['confidence_score']:.2f}</span>",
                        unsafe_allow_html=True,
                    )

                with col3:
                    st.write(f"🔍 {analysis['delusions_detected']}")

                with col4:
                    st.write(f"🔧 {analysis['recovery_actions']}")

                st.divider()
    else:
        st.info("No analyses found. Start your first analysis!")

    # Quick actions
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Start New Analysis", type="primary"):
            st.info("Redirecting to analysis page...")

    with col2:
        if st.button("📈 View All Results"):
            st.info("Redirecting to results page...")


def show_my_analyses(user_id: str):
    """Show user's analysis history"""
    st.header("📋 My Analyses")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox("Status", ["All", "completed", "error", "running"])

    with col2:
        confidence_filter = st.selectbox(
            "Confidence",
            ["All", "High (>0.8)", "Medium (0.6-0.8)", "Low (<0.6)"],
        )

    with col3:
        limit = st.slider("Show last N analyses", 10, 100, 20)

    # Get analyses
    analyses = get_user_analyses(user_id, limit=limit)

    # Apply filters
    if status_filter != "All":
        analyses = [a for a in analyses if a["status"] == status_filter]

    if confidence_filter != "All":
        if confidence_filter == "High (>0.8)":
            analyses = [a for a in analyses if a["confidence_score"] > 0.8]
        elif confidence_filter == "Medium (0.6-0.8)":
            analyses = [a for a in analyses if 0.6 <= a["confidence_score"] <= 0.8]
        elif confidence_filter == "Low (<0.6)":
            analyses = [a for a in analyses if a["confidence_score"] < 0.6]

    # Display analyses
    if analyses:
        for analysis in analyses:
            with st.expander(
                f"{analysis['project_path']} - {analysis['analysis_id'][:8]}...",
            ):
                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    st.write("**Project:**")
                    st.write(analysis["project_path"])

                with col2:
                    st.write("**Confidence:**")
                    confidence_color = (
                        "green"
                        if analysis["confidence_score"] > 0.8
                        else "orange"
                        if analysis["confidence_score"] > 0.6
                        else "red"
                    )
                    st.markdown(
                        f"<span style='color: {confidence_color}; font-weight: bold;'>{analysis['confidence_score']:.2f}</span>",
                        unsafe_allow_html=True,
                    )

                with col3:
                    st.write("**Delusions:**")
                    st.write(f"🔍 {analysis['delusions_detected']}")

                with col4:
                    st.write("**Recoveries:**")
                    st.write(f"🔧 {analysis['recovery_actions']}")

                with col5:
                    st.write("**Time:**")
                    st.write(f"⏱️ {analysis['processing_time']:.1f}s")

                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(
                        "View Details",
                        key=f"details_{analysis['analysis_id']}",
                    ):
                        st.session_state.selected_analysis = analysis["analysis_id"]
                        st.rerun()

                with col2:
                    if st.button(
                        "Download Report",
                        key=f"download_{analysis['analysis_id']}",
                    ):
                        st.info("Downloading report...")
    else:
        st.info("No analyses found matching the filters.")


def show_analysis_details():
    """Show detailed analysis results"""
    st.header("🔍 Analysis Details")

    # Analysis selector
    analysis_id = st.text_input("Enter Analysis ID:")

    if analysis_id:
        details = get_analysis_details(analysis_id)

        if details:
            # Basic info
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Confidence Score",
                    f"{details.get('confidence_score', 0):.2f}",
                )

            with col2:
                st.metric(
                    "Delusions Detected",
                    len(details.get("delusions_detected", [])),
                )

            with col3:
                st.metric("Recovery Actions", len(details.get("recovery_actions", [])))

            # Delusions details
            st.subheader("🔍 Detected Delusions")
            delusions = details.get("delusions_detected", [])
            if delusions:
                for i, delusion in enumerate(delusions):
                    with st.expander(
                        f"Delusion {i+1}: {delusion.get('type', 'Unknown')}",
                    ):
                        st.write(f"**File:** {delusion.get('file', 'Unknown')}")
                        st.write(
                            f"**Description:** {delusion.get('description', 'No description')}",
                        )
                        st.write(f"**Priority:** {delusion.get('priority', 'Unknown')}")
            else:
                st.success("No delusions detected! 🎉")

            # Recovery actions
            st.subheader("🔧 Recovery Actions")
            recoveries = details.get("recovery_actions", [])
            if recoveries:
                for i, recovery in enumerate(recoveries):
                    with st.expander(f"Recovery {i+1}"):
                        st.write(f"**Action:** {recovery.get('action', 'Unknown')}")
                        st.write(f"**File:** {recovery.get('file', 'Unknown')}")
                        st.write(f"**Status:** {recovery.get('status', 'Unknown')}")
            else:
                st.info("No recovery actions needed.")

            # Errors and warnings
            if details.get("errors"):
                st.subheader("❌ Errors")
                for error in details.get("errors", []):
                    st.error(error)

            if details.get("warnings"):
                st.subheader("⚠️ Warnings")
                for warning in details.get("warnings", []):
                    st.warning(warning)
        else:
            st.error("Analysis not found.")
    else:
        st.info("Enter an Analysis ID to view details.")


def show_real_time_updates():
    """Show real-time analysis updates"""
    st.header("⚡ Real-time Updates")

    # Mock real-time updates for demo
    st.info(
        "Real-time updates would be implemented with WebSocket connections to Pub/Sub.",
    )

    # Simulated updates
    updates = [
        {"analysis_id": "abc123", "progress": 25, "message": "Initializing agents..."},
        {
            "analysis_id": "def456",
            "progress": 50,
            "message": "Running security analysis...",
        },
        {"analysis_id": "ghi789", "progress": 75, "message": "Processing results..."},
        {"analysis_id": "abc123", "progress": 100, "message": "Analysis completed!"},
    ]

    for update in updates:
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])

            with col1:
                st.write(f"**{update['analysis_id'][:8]}...**")

            with col2:
                st.progress(update["progress"] / 100)
                st.caption(update["message"])

            with col3:
                st.write(f"{update['progress']}%")

            st.divider()


def show_settings():
    """Show user settings"""
    st.header("⚙️ Settings")

    # User preferences
    st.subheader("User Preferences")

    col1, col2 = st.columns(2)

    with col1:
        st.checkbox("Email notifications", value=True)
        st.checkbox("Real-time updates", value=True)
        st.checkbox("Auto-save results", value=True)

    with col2:
        st.selectbox("Default analysis priority", ["normal", "high", "low"])
        st.selectbox("Results per page", [10, 20, 50, 100])
        st.selectbox("Theme", ["light", "dark"])

    # API settings
    st.subheader("API Configuration")
    st.text_input("API Key", type="password")
    st.text_input("Webhook URL")

    # Save button
    if st.button("💾 Save Settings", type="primary"):
        st.success("Settings saved successfully!")


if __name__ == "__main__":
    main()
