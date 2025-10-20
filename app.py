import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import uuid
import socket
import os
import uuid

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


# Read query params (optional)
params = st.query_params
if params.get("page", [""])[0] == "home":
    if "role" in st.session_state:
        del st.session_state["role"]


# ==============================
#  SUPABASE CONFIGURATION
# ==============================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("⚠️ SUPABASE_URL or SUPABASE_KEY is not set in environment variables.")
    st.stop()

# Optional DNS check
try:
    host = SUPABASE_URL.replace("https://", "").split("/")[0]
    ip = socket.gethostbyname(host)
    print("Resolved Supabase host:", ip)
except socket.gaierror as e:
    st.error(f"DNS Resolution Failed: {e}")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==============================
#  DATABASE HELPER FUNCTIONS
# ==============================
def get_assessment(employee_name):
    response = (
        supabase.table("assessments")
        .select("*")
        .eq("employee_name", employee_name)
        .execute()
    )
    return response.data if response.data else None


def get_assessment_by_id(employee_id):
    if not employee_id:
        return None
    try:
        res = (
            supabase.table("assessments")
            .select("*")
            .eq("employee_id", employee_id)
            .execute()
        )
        return res.data if hasattr(res, "data") else None
    except Exception as e:
        st.error(f"Error fetching assessment by id: {e}")
        return None


def get_self_assessment(employee_id):
    if not is_valid_uuid(employee_id):
        st.error(f"❌ Employee ID '{employee_id}' is not valid.")
        return None
    try:
        res = (
            supabase.table("employee_self_assessments")
            .select("*")
            .eq("employee_id", employee_id)
            .execute()
        )
        return res.data if hasattr(res, "data") else None
    except Exception as e:
        st.error(f"Error fetching self-assessment: {e}")
        return None

def update_self_assessment(employee_id, data):
    if not is_valid_uuid(employee_id):
        st.error(f"❌ Employee ID '{employee_id}' is not valid. Cannot submit self-assessment.")
        return None

    try:
        existing = (
            supabase.table("employee_self_assessments")
            .select("*")
            .eq("employee_id", employee_id)
            .execute()
        )
        if existing and existing.data:
            res = (
                supabase.table("employee_self_assessments")
                .update(data)
                .eq("employee_id", employee_id)
                .execute()
            )
        else:
            res = (
                supabase.table("employee_self_assessments")
                .insert({"employee_id": employee_id, **data})
                .execute()
            )
        return res
    except Exception as e:
        st.error(f"Error updating/inserting self assessment: {e}")
        return None


def get_performance_assessment(employee_id):
    if not is_valid_uuid(employee_id):
        st.error(f"❌ Employee ID '{employee_id}' is not valid.")
        return None
    try:
        res = (
            supabase.table("annual_performance_assessments")
            .select("*")
            .eq("employee_id", employee_id)
            .execute()
        )
        return res.data if hasattr(res, "data") else None
    except Exception as e:
        st.error(f"Error fetching performance assessment: {e}")
        return None


def update_performance_assessment(employee_id, data):
    if not is_valid_uuid(employee_id):
        st.error(f"❌ Employee ID '{employee_id}' is not valid. Cannot submit evaluation.")
        return None
    
    try:
        # find assessments.id for this employee_id (so annual record can reference it)
        assessment_record = (
            supabase.table("assessments")
            .select("id")
            .eq("employee_id", employee_id)
            .execute()
        )

        if assessment_record.data and len(assessment_record.data) > 0:
            assessment_id = assessment_record.data[0].get("id")
        else:
            # If there is no linked assessments row for some reason, generate an uuid fallback.
            # Ideally you should ensure an assessments row exists for every employee_id.
            assessment_id = str(uuid.uuid4())

        data["assessment_id"] = assessment_id

        # keep only fields that exist in your annual_performance_assessments table
        valid_fields = [
            "employee_id",
            "assessment_id",
            "punctuality_score",
            "professional_attitude_score",
            "proactive_learning_score",
            "teamwork_collaboration_score",
            "commitment_loyalty_score",
            "strategic_alignment_score",
            "problem_solving_data_analysis_score",
            "communication_score",
            "interpersonal_skills_score",
            "technical_project_management_score",
            "manager_comments",
            "manager_signature",
            "manager_date",
            "created_at",
            "updated_at",
            "status",
        ]
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}

        existing = (
            supabase.table("annual_performance_assessments")
            .select("*")
            .eq("employee_id", employee_id)
            .execute()
        )

        if existing and existing.data:
            res = (
                supabase.table("annual_performance_assessments")
                .update(filtered_data)
                .eq("employee_id", employee_id)
                .execute()
            )
        else:
            res = (
                supabase.table("annual_performance_assessments")
                .insert(filtered_data)
                .execute()
            )
        return res
    except Exception as e:
        st.error(f"Error updating/inserting performance assessment: {e}")
        return None


def get_acknowledgment(employee_id):
    if not is_valid_uuid(employee_id):
        st.error(f"❌ Employee ID '{employee_id}' is not valid.")
        return None
    try:
        res = (
            supabase.table("acknowledgments")
            .select("*")
            .eq("employee_id", employee_id)
            .execute()
        )
        return res.data if hasattr(res, "data") else None
    except Exception as e:
        st.error(f"Error fetching acknowledgment: {e}")
        return None


def update_acknowledgment(employee_id, data):
    if not is_valid_uuid(employee_id):
        st.error(f"❌ Employee ID '{employee_id}' is not valid. Cannot submit acknowledgment.")
        return None
    
    try:
        # find assessments.id to include assessment_id if possible
        assessment_record = (
            supabase.table("assessments")
            .select("id")
            .eq("employee_id", employee_id)
            .execute()
        )
        assessment_id = assessment_record.data[0].get("id") if (assessment_record.data and len(assessment_record.data) > 0) else str(uuid.uuid4())

        # build payload according to your ack table columns
        payload = {
            "employee_id": employee_id,
            "assessment_id": assessment_id,
            "employee_comments": data.get("employee_comments", "Acknowledged"),
            "employee_signature": data.get("employee_signature", None),
            "employee_date": data.get("employee_date", datetime.utcnow().isoformat()),
        }

        existing = (
            supabase.table("acknowledgments")
            .select("*")
            .eq("employee_id", employee_id)
            .execute()
        )

        if existing and existing.data:
            # update the latest acknowledgment row (or all matching rows); here we update matching employee_id
            res = (
                supabase.table("acknowledgments")
                .update(payload)
                .eq("employee_id", employee_id)
                .execute()
            )
        else:
            res = (
                supabase.table("acknowledgments")
                .insert(payload)
                .execute()
            )
        return res
    except Exception as e:
        st.error(f"Error updating/inserting acknowledgment: {e}")
        return None


def create_or_update_assessment(employee_name, data, status=None):
    existing = get_assessment_by_id(data["employee_id"])
    if existing:
        update_data = data.copy()
        if status:
            update_data["status"] = status
        response = (
            supabase.table("assessments")
            .update(update_data)
            .eq("employee_id", data["employee_id"])
            .execute()
        )
    else:
        insert_data = {
            "employee_id": data["employee_id"],
            "employee_name": employee_name,
            "designation": data.get("designation", ""),
            "department": data.get("department", ""),
            "manager_name": data.get("manager_name", ""),
            "evaluation_period": data.get("evaluation_period", ""),
            "submission_date": datetime.now().date().isoformat(),
        }
        response = supabase.table("assessments").insert(insert_data).execute()
    return response


# ==============================
#  STREAMLIT APP
# ==============================
# from PIL import Image

# logo = Image.open("image.png")
# col1, col2, col3 = st.columns([2, 1, 2])
# with col2:
#     st.image(logo, width=120)

# st.markdown(
#     """
#     <h2 style='text-align: center;'>
#         Qubits Performance Review and Career Development
#     </h2>
#     """,
#     unsafe_allow_html=True
# )

# Display logo + title + optional back button in one line
col1, col2, col3 = st.columns([1, 6, 1])

with col1:
    if st.session_state.get("role") in ["employee", "manager"]:
        if st.button("< Back"):
            # Clear role and any other session variables
            for key in ["role", "show_manager_form", "show_add_employee"]:
                if key in st.session_state:
                    del st.session_state[key]

            # Rerun the app to go back to the home page
            st.rerun()



with col2:
    from PIL import Image

    logo = Image.open("image.png")
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.image(logo, width=120)

    st.markdown(
        """
        <h2 style='text-align: center;'>
            Qubits Performance Review and Career Development
        </h2>
        """,
        unsafe_allow_html=True
    )

with col3:
    # empty column to keep center alignment
    pass
    


# Role selection
if "role" not in st.session_state:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Employee"):
                st.session_state["role"] = "employee"
        with c2:
            if st.button("Manager"):
                st.session_state["role"] = "manager"



# MANAGER VIEW
elif st.session_state["role"] == "manager":
    manager_name = st.text_input("Manager Name", key="manager_name")
    if not manager_name:
        st.warning("Please enter your manager name to continue.")
        st.stop()

    st.markdown("### Employee Management")

    # --- Collapsible Add New Employee section ---
    if "show_add_employee" not in st.session_state:
        st.session_state.show_add_employee = False

    # Toggle button for collapsing
    if st.button("➕ Add New Employee" if not st.session_state.show_add_employee else "➖ Hide Add Employee Form"):
        st.session_state.show_add_employee = not st.session_state.show_add_employee

    # Show add employee form when expanded
    if st.session_state.show_add_employee:
        st.subheader("➕ Add New Employee")
        with st.form("add_employee_form"):
            employee_name = st.text_input("Employee Name", key="add_employee_name")
            employee_id = st.text_input("Employee ID (leave blank to auto-generate)", key="add_employee_id")
            designation = st.text_input("Designation")
            department = st.text_input("Department")
            evaluation_period = st.text_input("Evaluation Period", value="Aug 2024 to Aug 2025")

            submitted = st.form_submit_button("Add Employee")

            if submitted:
                if not employee_name:
                    st.error("Employee name is required.")
                    st.stop()

                if not employee_id:
                    employee_id = str(uuid.uuid4())
                    st.info(f"Auto-generated Employee ID: {employee_id}")
                else:
                    try:
                        uuid.UUID(employee_id)
                    except ValueError:
                        employee_id = str(uuid.uuid4())
                        st.warning("Invalid ID format — generated a new UUID.")

                create_or_update_assessment(employee_name, {
                    "employee_id": employee_id,
                    "designation": designation,
                    "department": department,
                    "manager_name": manager_name,
                    "evaluation_period": evaluation_period
                })
                st.success(f"✅ Employee **{employee_name}** added successfully!")

    st.markdown("---")
    st.subheader("Review Employee Performance")

    # --- Fetch employees assigned to this manager ---
    assessments = (
        supabase.table("assessments")
        .select("*")
        .eq("manager_name", manager_name)
        .execute()
        .data
    )

    if assessments:
        # Add an empty placeholder first
        employee_names = ["-- Select an employee --"] + [a["employee_name"] for a in assessments]
        selected_emp = st.selectbox("Select an employee to review", employee_names)

        # Only run the following if a real employee is selected
        if selected_emp != "-- Select an employee --":
            emp_record = next((a for a in assessments if a["employee_name"] == selected_emp), None)
            if emp_record:
                employee_id = emp_record.get("employee_id")

                col1, col2 = st.columns(2)
                with col1:
                    review_btn = st.button("Review Employee’s Filled Form")
                with col2:
                    fill_btn = st.button("Fill Manager’s Evaluation Form")

                if review_btn:
                    st.subheader("Employee’s Submitted Self-Assessment")
                    self_data = get_self_assessment(employee_id)
                    if self_data:
                        self_record = self_data[0]
                        for key, value in self_record.items():
                            if key not in ["employee_id", "assessmentid", "created_at", "updated_at"]:
                                st.markdown(f"**{key.replace('_', ' ').title()}:**")
                                st.write(value)
                                st.markdown("---")
                    else:
                        st.info("Employee has not submitted their self-assessment yet.")

                if fill_btn:
                    st.session_state["show_manager_form"] = True

                if st.session_state.get("show_manager_form", False):
                    st.subheader("Manager’s Evaluation Form")
                    with st.form("manager_eval_form", clear_on_submit=True):
                        st.markdown("### Evaluation Criteria (Rate 1–10)")

                        punctuality_score = st.slider("Punctuality", 1, 10, 5)
                        professional_attitude_score = st.slider("Professional Attitude", 1, 10, 5)
                        proactive_learning_score = st.slider("Proactive Learning", 1, 10, 5)
                        teamwork_collaboration_score = st.slider("Teamwork & Collaboration", 1, 10, 5)
                        commitment_loyalty_score = st.slider("Commitment & Loyalty", 1, 10, 5)
                        strategic_alignment_score = st.slider("Strategic Alignment", 1, 10, 5)
                        problem_solving_data_analysis_score = st.slider("Problem Solving & Data Analysis", 1, 10, 5)
                        communication_score = st.slider("Communication", 1, 10, 5)
                        interpersonal_skills_score = st.slider("Interpersonal Skills", 1, 10, 5)
                        technical_project_management_score = st.slider("Technical/Project Management", 1, 10, 5)

                        manager_comments = st.text_area("Manager Comments")
                        manager_signature = st.text_input("Manager Signature")
                        manager_date = st.date_input("Date", datetime.now().date())

                        submitted_eval = st.form_submit_button("Submit Evaluation")

                        if submitted_eval:
                            data = {
                                "employee_id": employee_id,
                                "punctuality_score": punctuality_score,
                                "professional_attitude_score": professional_attitude_score,
                                "proactive_learning_score": proactive_learning_score,
                                "teamwork_collaboration_score": teamwork_collaboration_score,
                                "commitment_loyalty_score": commitment_loyalty_score,
                                "strategic_alignment_score": strategic_alignment_score,
                                "problem_solving_data_analysis_score": problem_solving_data_analysis_score,
                                "communication_score": communication_score,
                                "interpersonal_skills_score": interpersonal_skills_score,
                                "technical_project_management_score": technical_project_management_score,
                                "manager_comments": manager_comments,
                                "manager_signature": manager_signature,
                                "manager_date": str(manager_date),
                                "created_at": datetime.utcnow().isoformat(),
                                "updated_at": datetime.utcnow().isoformat(),
                            }
                            try:
                                res = update_performance_assessment(employee_id, data)
                                if res and getattr(res, "status_code", None) in (200, 201, 204) or (res and hasattr(res, "data")):
                                    st.success(f"✅ Evaluation for **{selected_emp}** submitted successfully!")
                                    st.balloons()
                                    st.session_state["show_manager_form"] = False
                                else:
                                    st.warning("Evaluation saved but no data returned from Supabase.")
                            except Exception as e:
                                st.error(f"Error saving evaluation: {e}")

                # --- Show Acknowledgment Status ---
                ack_data = supabase.table("acknowledgments").select("*").eq("employee_id", employee_id).execute()
                if ack_data.data:
                    ack = ack_data.data[0]
                    st.success(f"✅ Employee acknowledged the evaluation on {ack.get('employee_date', '—')}")
                else:
                    pass
    else:
        st.info("No employees assigned to you yet.")

    


# EMPLOYEE VIEW
# ==============================
# EMPLOYEE VIEW
# ==============================
elif st.session_state["role"] == "employee":
    employee_name = st.text_input("Employee Name")
    employee_id = st.text_input("Employee ID")

    if not employee_name or not employee_id:
        st.warning("Please enter both Employee Name and ID.")
        st.stop()

    assessment_list = get_assessment(employee_name)
    assessment = assessment_list[0] if assessment_list else None

    if not assessment:
        st.info("No existing record found. Please fill initial details.")
        with st.form("initial_employee_form"):
            designation = st.text_input("Designation")
            department = st.text_input("Department")
            manager_name = st.text_input("Manager Name")
            evaluation_period = st.text_input("Evaluation Period", value="Aug 2024 to Aug 2025")
            submitted = st.form_submit_button("Submit Details")

            if submitted:
                try:
                    uuid.UUID(employee_id)
                except ValueError:
                    employee_id = str(uuid.uuid4())
                    st.warning("Invalid Employee ID format — generated a new one.")

                create_or_update_assessment(employee_name, {
                    "employee_id": employee_id,
                    "designation": designation,
                    "department": department,
                    "manager_name": manager_name,
                    "evaluation_period": evaluation_period
                })
                st.success("✅ Initial record created! Please reload the page.")
                st.stop()

    # =============================
    # Check existing submissions
    # =============================
    existing_self = get_self_assessment(employee_id)
    perf_data = get_performance_assessment(employee_id)
    ack_data = get_acknowledgment(employee_id)

    has_self_submitted = bool(existing_self)
    has_manager_review = bool(perf_data)
    has_acknowledged = bool(ack_data and ack_data[0].get("acknowledged"))

    # =============================
    # CASE 1 — Employee not yet submitted self assessment
    # =============================
    if not has_self_submitted:
        st.header("Employee Self Assessment")
        self_data = {
            "top_achievements": st.text_area("Top 3–5 Key Achievements"),
            "goals_accomplished": st.text_area("Goals or Targets Accomplished"),
            "value_added": st.text_area("How did your work add value?"),
            "new_skills_gained": st.text_area("New Skills Gained"),
            "certifications_completed": st.text_area("Certifications or Training"),
            "skills_to_improve": st.text_area("Skills to Improve Next Year"),
            "challenges_faced": st.text_area("Challenges Faced"),
            "how_overcame_challenges": st.text_area("How You Overcame Challenges"),
            "support_needed": st.text_area("Support Needed from Company"),
            "why_deserve_increment": st.text_area("Why You Deserve a Salary Increment (Optional)"),
            "unique_value": st.text_area("Unique Value You Bring (Optional)")
        }

        if st.button("Submit Self Assessment"):
            update_self_assessment(employee_id, self_data)
            create_or_update_assessment(employee_name, {"employee_id": employee_id}, "employee_submitted")
            st.success("✅ Self Assessment Submitted Successfully! Please wait for your manager’s review.")
            st.stop()

    # =============================
    # CASE 2 — Self assessment submitted
    # =============================
    else:
        st.success("✅ You have already submitted your self-assessment.")

        # CASE 2A — Manager has given feedback but employee hasn’t acknowledged yet
        if has_manager_review and not has_acknowledged:
            st.subheader("Manager’s Evaluation Feedback")

            feedback = perf_data[0]
            st.markdown(f"**Punctuality:** {feedback.get('punctuality_score', '—')}")
            st.markdown(f"**Professional Attitude:** {feedback.get('professional_attitude_score', '—')}")
            st.markdown(f"**Proactive Learning:** {feedback.get('proactive_learning_score', '—')}")
            st.markdown(f"**Teamwork & Collaboration:** {feedback.get('teamwork_collaboration_score', '—')}")
            st.markdown(f"**Commitment & Loyalty:** {feedback.get('commitment_loyalty_score', '—')}")
            st.markdown(f"**Strategic Alignment:** {feedback.get('strategic_alignment_score', '—')}")
            st.markdown(f"**Problem Solving & Data Analysis:** {feedback.get('problem_solving_data_analysis_score', '—')}")
            st.markdown(f"**Communication:** {feedback.get('communication_score', '—')}")
            st.markdown(f"**Interpersonal Skills:** {feedback.get('interpersonal_skills_score', '—')}")
            st.markdown(f"**Technical/Project Management:** {feedback.get('technical_project_management_score', '—')}")
            st.markdown(f"**Manager Comments:** {feedback.get('manager_comments', '—')}")
            st.markdown(f"**Reviewed On:** {feedback.get('manager_date', '—')}")

            with st.form("ack_form"):
                ack = st.checkbox("✅ I acknowledge that I have reviewed my manager’s evaluation.")
                ack_submit = st.form_submit_button("Submit Acknowledgment")

                if ack_submit and ack:
                    update_acknowledgment(
                        employee_id,
                        {"acknowledged": True, "ack_date": datetime.now().isoformat()},
                    )
                    st.success("✅ Acknowledgment recorded successfully!")
                    st.balloons()
                    st.stop()

        # CASE 2B — Already acknowledged
        elif has_acknowledged:
            st.info("✅ You have already acknowledged your manager’s evaluation. Thank you!")

        # CASE 2C — Self-assessment submitted but manager not yet reviewed
        else:
            st.info("⌛ Your manager has not yet completed the evaluation. Please check back later.")
    # ==============================
    # MANAGER’S EVALUATION FEEDBACK (proper display)
    # ==============================
    if assessment:
        perf_data = get_performance_assessment(assessment["employee_id"])
        if perf_data:
            manager_feedback = perf_data[0]
            st.subheader("Manager’s Evaluation Feedback")

            # mapping label -> column name
            field_labels = {
                "punctuality_score": "Punctuality",
                "professional_attitude_score": "Professional Attitude",
                "proactive_learning_score": "Proactive Learning",
                "teamwork_collaboration_score": "Teamwork & Collaboration",
                "commitment_loyalty_score": "Commitment & Loyalty",
                "strategic_alignment_score": "Strategic Alignment",
                "problem_solving_data_analysis_score": "Problem Solving & Data Analysis",
                "communication_score": "Communication",
                "interpersonal_skills_score": "Interpersonal Skills",
                "technical_project_management_score": "Technical / Project Management",
                "manager_comments": "Manager Comments",
                "manager_date": "Reviewed On",
            }

            for col, label in field_labels.items():
                val = manager_feedback.get(col)
                # show '—' for missing/empty values
                display_val = val if (val is not None and str(val).strip() != "") else "—"
                st.write(f"**{label}:** {display_val}")

            st.markdown("---")

            # Acknowledgement: check if user already acknowledged by presence of acknowledgment row
            ack_rows = get_acknowledgment(assessment["employee_id"])
            already_ack = False
            if ack_rows:
                # if there's a row and employee_comments contains 'Acknowledged', consider it acknowledged
                for r in ack_rows:
                    if r.get("employee_comments") and "acknow" in str(r.get("employee_comments")).lower():
                        already_ack = True
                        break
                # if any ack row exists we can consider it acknowledged too (adjust as you prefer)
                if not already_ack and len(ack_rows) > 0:
                    # If you want stricter check, change this logic; for now presence of a row is sufficient
                    already_ack = any([True for r in ack_rows if r.get("employee_comments")])

            if not already_ack:
                with st.form("ack_form"):
                    ack = st.checkbox("I acknowledge that I have reviewed my manager’s evaluation.")
                    signature = st.text_input("Signature (optional)")
                    ack_submit = st.form_submit_button("Submit Acknowledgment")

                    if ack_submit:
                        if ack:
                            ack_payload = {
                                "employee_comments": "Acknowledged",
                                "employee_signature": signature if signature else None,
                                "employee_date": datetime.utcnow().isoformat(),
                            }
                            update_acknowledgment(assessment["employee_id"], ack_payload)
                            st.success("✅ Acknowledgment recorded. Thank you!")
                        else:
                            st.warning("Please check the acknowledgment box before submitting.")
            else:
                st.success("✅ You have already acknowledged this evaluation.")
        else:
            st.info("Manager has not submitted the evaluation yet.")
