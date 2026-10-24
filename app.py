import streamlit as st
import pandas as pd
import numpy as np
import os
import joblib

# Page Configuration
st.set_page_config(
    page_title="AI Approval Management System",
    page_icon="📋",
    layout="wide"
)

# Sidebar Menu
st.sidebar.title("Approval Dashboard")
app_mode = st.sidebar.radio(
    "Choose Module",
    ["💼 Expense Approval", "🏖️ Leave Approval Management"]
)

# =========================================================
# MODULE 1: EXPENSE APPROVAL
# =========================================================
if app_mode == "💼 Expense Approval":
    st.title("💼 AI Expense Approval System")
    st.markdown("Automated budget verification and risk approval.")
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        amount = st.number_input("Request Amount (₹)", min_value=100, max_value=200000, value=15000, step=500)
        department = st.selectbox("Department", ["Sales", "IT", "HR", "Operations", "Finance"])
        role_level = st.slider("Employee Experience Level (1-10)", 1, 10, 3)

    with col2:
        category = st.selectbox("Expense Category", ["Equipment", "Medical", "Travel", "Training"])
        days_notice = st.number_input("Notice Period (Days)", min_value=1, max_value=60, value=10)

    st.write("")
    if st.button("Evaluate Expense Request", type="primary"):
        model_path = os.path.join("models", "approval_model.pkl")
        cols_path = os.path.join("models", "model_columns.pkl")

        if os.path.exists(model_path):
            try:
                model = joblib.load(model_path)
                input_df = pd.DataFrame([{
                    "Amount": amount,
                    "Department": department,
                    "Role_Level": role_level,
                    "Category": category,
                    "Days_Notice": days_notice
                }])
                input_encoded = pd.get_dummies(input_df)

                if os.path.exists(cols_path):
                    saved_cols = joblib.load(cols_path)
                    input_encoded = input_encoded.reindex(columns=saved_cols, fill_value=0)

                pred = model.predict(input_encoded)[0]
                if pred == 1:
                    st.success("✅ **Request Status: APPROVED** (Passed standard policy checks)")
                else:
                    st.error("❌ **Request Status: REJECTED / ESCALATED** (Requires Management Review)")
            except Exception:
                if amount > 40000 and days_notice < 7:
                    st.error("❌ **Request Rejected**: High amount requested with very low notice period.")
                else:
                    st.success("✅ **Request Approved**: Verified under operational limits.")
        else:
            if amount > 40000 and days_notice < 7:
                st.error("❌ **Request Rejected**: High amount requested with very low notice period.")
            else:
                st.success("✅ **Request Approved**: Verified under operational limits.")


# =========================================================
# MODULE 2: LEAVE APPROVAL MANAGEMENT
# =========================================================
elif app_mode == "🏖️ Leave Approval Management":
    st.title("🏖️ AI Leave Approval System")
    st.markdown("Smart leave management with policy validation and reason checking.")
    st.divider()

    # Leave Guidelines & Templates
    reason_guidelines = {
        "Medical / Sick Leave": {
            "guide": "ℹ️ 2+ days sick leave-ku doctor prescription / medical proof thevai.",
            "placeholder": "e.g., Suffering from viral fever and severe cold. Doctor advised 2 days bed rest.",
            "min_days": 1
        },
        "Family Emergency": {
            "guide": "ℹ️ Unplanned urgent hospital visit, critical family support, or accident emergencies.",
            "placeholder": "e.g., Need to attend an urgent family medical emergency in native place.",
            "min_days": 1
        },
        "Family Function / Wedding": {
            "guide": "ℹ️ Family wedding, house warming or personal rituals. 3 days munnadiye apply pannanum.",
            "placeholder": "e.g., Attending my sister's wedding ceremony and related family events.",
            "min_days": 1
        },
        "Exam / Academic Project": {
            "guide": "ℹ️ Semester exams, certifications, viva, or final project evaluation.",
            "placeholder": "e.g., Appearing for university end-semester examinations and practical viva.",
            "min_days": 1
        },
        "Personal Travel / Out of Station": {
            "guide": "ℹ️ Planned vacation or travel. Critical release time-la apply panna koodathu.",
            "placeholder": "e.g., Traveling to native place for essential personal documentation work.",
            "min_days": 1
        }
    }

    col1, col2 = st.columns(2)

    with col1:
        emp_id = st.text_input("Employee ID / Name", value="EMP-2041")
        dept = st.selectbox("Department", ["IT", "Sales", "HR", "Operations", "Finance"], key="leave_dept")
        leave_days = st.number_input("Number of Days Requested", min_value=1, max_value=30, value=2)
        available_balance = st.number_input("Available Leave Balance", min_value=0, max_value=40, value=8)

    with col2:
        selected_cat = st.selectbox("1. Select Leave Category / Reason Type", list(reason_guidelines.keys()))
        
        # Guide message
        st.info(reason_guidelines[selected_cat]["guide"])
        
        # Input box with placeholder
        detailed_reason = st.text_area(
            "2. Detailed Reason / Explanation",
            placeholder=reason_guidelines[selected_cat]["placeholder"],
            height=110
        )
        critical_sprint = st.radio("Is there an ongoing critical deadline / sprint?", ["No", "Yes"], horizontal=True)

    st.write("")
    if st.button("Submit Leave Request", type="primary"):
        invalid_words = ["movie", "cinema", "sleeping", "bored", "lazy", "pubg", "party", "trip with friends"]
        
        # Validations
        if not detailed_reason.strip():
            st.error("⚠️ Reason box empty-a irukku. Please brief explanation kudunga!")
            
        elif any(bad_word in detailed_reason.lower() for bad_word in invalid_words):
            st.error("❌ **Request Rejected by AI**: Casual / Non-official reason enter panreenga. Genuine reason specify pannunga.")
            
        elif leave_days > available_balance:
            st.error(f"❌ **Request Rejected**: Insufficient leave balance! (Requested: {leave_days}, Balance: {available_balance}).")
            
        elif critical_sprint == "Yes" and selected_cat not in ["Medical / Sick Leave", "Family Emergency"]:
            st.warning("⚠️ **Escalated to Manager**: Critical sprint-la normal leave direct-a approve aagathu. Manager manual review thevai.")
            
        elif selected_cat == "Medical / Sick Leave" and leave_days > 2 and ("doctor" not in detailed_reason.lower() and "hospital" not in detailed_reason.lower()):
            st.warning("⚠️ **Conditionally Approved**: 2 days-ku mela sick leave edukkrathala medical certificate upload pannanum.")
            
        else:
            remaining = available_balance - leave_days
            st.success(
                f"✅ **Leave Request Approved by AI!**\n\n"
                f"- **Employee:** {emp_id}\n"
                f"- **Category:** {selected_cat}\n"
                f"- **Approved Days:** {leave_days}\n"
                f"- **Submitted Reason:** {detailed_reason}\n"
                f"- **Remaining Balance:** {remaining} days"
            )
            st.balloons()