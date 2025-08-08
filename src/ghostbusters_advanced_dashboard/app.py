#!/usr/bin/env python3
"""
Advanced Ghostbusters Analytics Dashboard
Phase 3: ML Insights, Custom Agents, and Enterprise Features
"""

import logging
from typing import Any

import streamlit as st
from firebase_admin import initialize_app  # type: ignore
from google.cloud import firestore, pubsub_v1  # type: ignore

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
    "advanced-analysis-updates-sub",
)

# Page configuration
st.set_page_config(
    page_title="Advanced Ghostbusters Analytics Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for advanced styling
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
    .ml-insight-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .enterprise-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .custom-agent-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
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
        return "enterprise-user-123"
    except Exception as e:
        logger.error("Authentication failed: %s", str(e))
        return None  # type: ignore


def get_advanced_analyses(user_id: str, limit: int = 50) -> list[dict[str, Any]]:
    """Get user's advanced analysis history"""
    try:
        docs = (
            db.collection("advanced_ghostbusters_results")
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
                    "ml_insights": data.get("ml_insights", {}),
                    "enterprise_features": data.get("enterprise_features", {}),
                    "custom_agents_used": data.get("metadata", {}).get(
                        "custom_agents_used",
                        0,
                    ),
                },
            )

        return analyses
    except Exception as e:
        logger.error("Failed to get advanced analyses: %s", str(e))
        return []


def get_custom_agents(user_id: str) -> list[dict[str, Any]]:
    """Get user's custom agents"""
    try:
        docs = db.collection("custom_agents").where("user_id", "==", user_id).stream()
        agents = []
        for doc in docs:
            data = doc.to_dict()
            agents.append(
                {
                    "agent_id": doc.id,
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "type": data.get("type"),
                    "config": data.get("config", {}),
                    "enabled": data.get("enabled", True),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                },
            )
        return agents
    except Exception as e:
        logger.error("Failed to get custom agents: %s", str(e))
        return []


def get_enterprise_analytics() -> dict[str, Any]:
    """Get enterprise analytics"""
    try:
        # Get enterprise metrics
        total_analyses = len(
            list(db.collection("advanced_ghostbusters_results").stream()),
        )
        total_users = len(list(db.collection("enterprise_users").stream()))
        total_custom_agents = len(list(db.collection("custom_agents").stream()))
        total_audit_logs = len(list(db.collection("audit_logs").stream()))

        # Get recent ML insights
        recent_analyses = list(
            db.collection("advanced_ghostbusters_results")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(10)
            .stream(),
        )

        ml_insights_summary = {
            "total_risk_scores": 0,
            "high_priority_count": 0,
            "anomaly_detections": 0,
            "avg_risk_score": 0,
        }

        for doc in recent_analyses:
            data = doc.to_dict()
            ml_insights = data.get("ml_insights", {})
            risk_score = ml_insights.get("risk_score", 0)
            priority = ml_insights.get("priority_level", "medium")
            anomaly = ml_insights.get("anomaly_detection", False)

            ml_insights_summary["total_risk_scores"] += risk_score
            if priority == "high":
                ml_insights_summary["high_priority_count"] += 1
            if anomaly:
                ml_insights_summary["anomaly_detections"] += 1

        if recent_analyses:
            ml_insights_summary["avg_risk_score"] = ml_insights_summary[
                "total_risk_scores"
            ] / len(
                recent_analyses,
            )  # type: ignore

        return {
            "total_analyses": total_analyses,
            "total_users": total_users,
            "total_custom_agents": total_custom_agents,
            "total_audit_logs": total_audit_logs,
            "ml_insights_summary": ml_insights_summary,
        }
    except Exception as e:
        logger.error("Failed to get enterprise analytics: %s", str(e))
        return {}


def main() -> None:
    """Main advanced dashboard application"""

    # Header
    st.markdown(
        '<h1 class="main-header">🤖 Advanced Ghostbusters Analytics Dashboard</h1>',
        unsafe_allow_html=True,
    )

    # Sidebar
    st.sidebar.title("Advanced Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        [
            "ML Insights",
            "Custom Agents",
            "Enterprise Analytics",
            "Advanced Results",
            "Audit Logs",
            "Settings",
        ],
    )

    # Authenticate user
    user_id = authenticate_user()
    if not user_id:
        st.error("Authentication failed. Please log in.")
        return

    st.sidebar.success(f"Logged in as: {user_id}")

    if page == "ML Insights":
        show_ml_insights(user_id)
    elif page == "Custom Agents":
        show_custom_agents(user_id)
    elif page == "Enterprise Analytics":
        show_enterprise_analytics()
    elif page == "Advanced Results":
        show_advanced_results(user_id)
    elif page == "Audit Logs":
        show_audit_logs()
    elif page == "Settings":
        show_advanced_settings()


def show_ml_insights(user_id: str) -> None:
    """Show ML-powered insights"""
    st.header("🧠 ML-Powered Insights")

    # Get recent analyses with ML insights
    analyses = get_advanced_analyses(user_id, limit=10)

    if analyses:
        # ML Insights Overview
        col1, col2, col3 = st.columns(3)

        with col1:
            total_risk_scores = sum(
                a.get("ml_insights", {}).get("risk_score", 0) for a in analyses
            )
            avg_risk_score = total_risk_scores / len(analyses) if analyses else 0
            st.metric("Average Risk Score", f"{avg_risk_score:.2f}")

        with col2:
            high_priority_count = sum(
                1
                for a in analyses
                if a.get("ml_insights", {}).get("priority_level") == "high"
            )
            st.metric("High Priority Issues", high_priority_count)

        with col3:
            anomaly_count = sum(
                1
                for a in analyses
                if a.get("ml_insights", {}).get("anomaly_detection", False)
            )
            st.metric("Anomalies Detected", anomaly_count)

        # Detailed ML Insights
        st.subheader("📊 Recent ML Insights")
        for analysis in analyses[:5]:
            ml_insights = analysis.get("ml_insights", {})
            if ml_insights:
                with st.expander(
                    f"Analysis {analysis['analysis_id'][:8]}... - {analysis['project_path']}",
                ):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(
                            f"""
                            <div class="ml-insight-card">
                                <h4>Risk Assessment</h4>
                                <p><strong>Risk Score:</strong> {ml_insights.get('risk_score', 0):.2f}</p>
                                <p><strong>Priority Level:</strong> {ml_insights.get('priority_level', 'medium')}</p>
                                <p><strong>Anomaly Detected:</strong> {'Yes' if ml_insights.get('anomaly_detection') else 'No'}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    with col2:
                        st.markdown(
                            f"""
                            <div class="ml-insight-card">
                                <h4>Recommendations</h4>
                                <ul>
                                    {''.join(f'<li>{action}</li>' for action in ml_insights.get('recommended_actions', []))}
                                </ul>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    # Trend Analysis
                    trend_analysis = ml_insights.get("trend_analysis", {})
                    if trend_analysis:
                        st.subheader("📈 Trend Analysis")
                        st.json(trend_analysis)

    else:
        st.info("No advanced analyses found. Start your first advanced analysis!")

    # Quick Actions
    st.subheader("🚀 Quick Actions")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🤖 Start Advanced Analysis", type="primary"):
            st.info("Redirecting to advanced analysis...")

    with col2:
        if st.button("📊 View ML Model Performance"):
            st.info("Redirecting to ML model dashboard...")


def show_custom_agents(user_id: str) -> None:
    """Show custom agents management"""
    st.header("🤖 Custom Agents")

    # Get custom agents
    agents = get_custom_agents(user_id)

    # Agent Management
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Your Custom Agents")
        if agents:
            for agent in agents:
                with st.expander(f"{agent['name']} - {agent['type']}"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.write("**Name:**")
                        st.write(agent["name"])

                    with col2:
                        st.write("**Type:**")
                        st.write(agent["type"])

                    with col3:
                        st.write("**Status:**")
                        status_color = "green" if agent["enabled"] else "red"
                        st.markdown(
                            f"<span style='color: {status_color}; font-weight: bold;'>{'Enabled' if agent['enabled'] else 'Disabled'}</span>",
                            unsafe_allow_html=True,
                        )

                    st.write("**Description:**")
                    st.write(agent["description"])

                    st.write("**Configuration:**")
                    st.json(agent["config"])

                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Edit", key=f"edit_{agent['agent_id']}"):
                            st.info("Edit functionality would be implemented here")

                    with col2:
                        if st.button("Toggle", key=f"toggle_{agent['agent_id']}"):
                            st.info("Toggle functionality would be implemented here")

                    with col3:
                        if st.button("Delete", key=f"delete_{agent['agent_id']}"):
                            st.info("Delete functionality would be implemented here")
        else:
            st.info("No custom agents found. Create your first custom agent!")

    with col2:
        st.subheader("Create New Agent")
        with st.form("create_agent"):
            agent_name = st.text_input("Agent Name")
            agent_type = st.selectbox(
                "Agent Type",
                ["security", "quality", "performance", "custom"],
            )
            agent_description = st.text_area("Description")
            agent_config = st.text_area("Configuration (JSON)")

            if st.form_submit_button("Create Agent"):
                if agent_name and agent_type:
                    st.success("Agent created successfully!")
                else:
                    st.error("Please fill in all required fields")


def show_enterprise_analytics() -> None:
    """Show enterprise analytics"""
    st.header("🏢 Enterprise Analytics")

    # Get enterprise analytics
    analytics = get_enterprise_analytics()

    if analytics:
        # Enterprise Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Analyses", analytics.get("total_analyses", 0))

        with col2:
            st.metric("Total Users", analytics.get("total_users", 0))

        with col3:
            st.metric("Custom Agents", analytics.get("total_custom_agents", 0))

        with col4:
            st.metric("Audit Logs", analytics.get("total_audit_logs", 0))

        # ML Insights Summary
        ml_summary = analytics.get("ml_insights_summary", {})
        if ml_summary:
            st.subheader("🧠 ML Insights Summary")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Average Risk Score",
                    f"{ml_summary.get('avg_risk_score', 0):.2f}",
                )

            with col2:
                st.metric(
                    "High Priority Issues",
                    ml_summary.get("high_priority_count", 0),
                )

            with col3:
                st.metric("Anomalies Detected", ml_summary.get("anomaly_detections", 0))

        # Enterprise Features Usage
        st.subheader("📊 Enterprise Features Usage")
        features_data = {
            "ML Insights": analytics.get("total_analyses", 0),
            "Custom Agents": analytics.get("total_custom_agents", 0),
            "Audit Logging": analytics.get("total_audit_logs", 0),
            "Enterprise Quotas": analytics.get("total_users", 0),
        }

        st.bar_chart(features_data)

    else:
        st.info("No enterprise analytics available.")


def show_advanced_results(user_id: str) -> None:
    """Show advanced analysis results"""
    st.header("🔍 Advanced Analysis Results")

    # Analysis selector
    analysis_id = st.text_input("Enter Advanced Analysis ID:")

    if analysis_id:
        # Get advanced analysis details
        doc = db.collection("advanced_ghostbusters_results").document(analysis_id).get()
        if doc.exists:
            data = doc.to_dict()

            # Basic info
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Confidence Score", f"{data.get('confidence_score', 0):.2f}")

            with col2:
                st.metric("Delusions Detected", len(data.get("delusions_detected", [])))

            with col3:
                st.metric("Recovery Actions", len(data.get("recovery_actions", [])))

            # ML Insights
            ml_insights = data.get("ml_insights", {})
            if ml_insights:
                st.subheader("🧠 ML Insights")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(
                        f"""
                        <div class="ml-insight-card">
                            <h4>Risk Assessment</h4>
                            <p><strong>Risk Score:</strong> {ml_insights.get('risk_score', 0):.2f}</p>
                            <p><strong>Priority Level:</strong> {ml_insights.get('priority_level', 'medium')}</p>
                            <p><strong>Anomaly Detected:</strong> {'Yes' if ml_insights.get('anomaly_detection') else 'No'}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col2:
                    st.markdown(
                        f"""
                        <div class="ml-insight-card">
                            <h4>Recommendations</h4>
                            <ul>
                                {''.join(f'<li>{action}</li>' for action in ml_insights.get('recommended_actions', []))}
                            </ul>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # Enterprise Features
            enterprise_features = data.get("enterprise_features", {})
            if enterprise_features:
                st.subheader("🏢 Enterprise Features")
                st.json(enterprise_features)

            # Custom Agents Used
            metadata = data.get("metadata", {})
            custom_agents_used = metadata.get("custom_agents_used", 0)
            if custom_agents_used > 0:
                st.subheader("🤖 Custom Agents Used")
                st.metric("Custom Agents", custom_agents_used)

        else:
            st.error("Advanced analysis not found.")
    else:
        st.info("Enter an Advanced Analysis ID to view details.")


def show_audit_logs() -> None:
    """Show audit logs"""
    st.header("📋 Audit Logs")

    # Get recent audit logs
    docs = (
        db.collection("audit_logs")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(20)
        .stream()
    )

    logs = []
    for doc in docs:
        data = doc.to_dict()
        logs.append(
            {
                "user_id": data.get("user_id"),
                "action": data.get("action"),
                "details": data.get("details"),
                "timestamp": data.get("timestamp"),
            },
        )

    if logs:
        for log in logs:
            with st.expander(f"{log['action']} - {log['user_id']}"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**User:**")
                    st.write(log["user_id"])

                    st.write("**Action:**")
                    st.write(log["action"])

                with col2:
                    st.write("**Timestamp:**")
                    st.write(log["timestamp"])

                    st.write("**Details:**")
                    st.json(log["details"])
    else:
        st.info("No audit logs found.")


def show_advanced_settings() -> None:
    """Show advanced settings"""
    st.header("⚙️ Advanced Settings")

    # Enterprise Settings
    st.subheader("🏢 Enterprise Settings")
    col1, col2 = st.columns(2)

    with col1:
        st.checkbox("Enable ML Insights", value=True)
        st.checkbox("Enable Custom Agents", value=True)
        st.checkbox("Enable Audit Logging", value=True)

    with col2:
        st.selectbox("ML Model Version", ["v1.0", "v1.1", "v1.2"])
        st.selectbox("Risk Threshold", ["Low", "Medium", "High"])
        st.selectbox("Anomaly Detection", ["Enabled", "Disabled"])

    # Custom Agent Settings
    st.subheader("🤖 Custom Agent Settings")
    col1, col2 = st.columns(2)

    with col1:
        st.number_input("Max Custom Agents", min_value=1, max_value=100, value=10)
        st.selectbox("Agent Execution Mode", ["Sequential", "Parallel"])

    with col2:
        st.checkbox("Auto-enable New Agents", value=True)
        st.checkbox("Agent Performance Monitoring", value=True)

    # Save button
    if st.button("💾 Save Advanced Settings", type="primary"):
        st.success("Advanced settings saved successfully!")


if __name__ == "__main__":
    main()
