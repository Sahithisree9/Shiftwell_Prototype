import streamlit as st
from datetime import date, timedelta

st.set_page_config(page_title="Shiftwell Smart Approvals", page_icon="🗓️", layout="wide")
st.title("Shiftwell | Smart Shift Approvals")
st.caption("Product case prototype · Simulated data · Not connected to customer systems")

with st.sidebar:
    st.header("Policy settings")
    weekly_limit = st.number_input("Weekly-hours approval threshold", min_value=1, max_value=100, value=48, step=1)
    auto_approve = st.toggle("Auto-approve eligible swaps", value=True)
    warning_days = st.number_input("Certificate expiry warning window (days)", min_value=1, max_value=90, value=30)
    st.divider()
    st.caption("Demonstration only. Production policy must be configured and approved per customer.")

today = date.today()
employees = [
    {"name":"Ananya Rao", "role":"Nurse", "credential":"BLS", "expiry":today-timedelta(days=4), "hours":42, "trained":True},
    {"name":"Meera Shah", "role":"Nurse", "credential":"BLS", "expiry":today+timedelta(days=18), "hours":36, "trained":True},
    {"name":"Ravi Kumar", "role":"Cook", "credential":"Food Safety", "expiry":today+timedelta(days=120), "hours":44, "trained":True},
    {"name":"Kiran Das", "role":"Store Associate", "credential":"Role Training", "expiry":today+timedelta(days=240), "hours":32, "trained":False},
]
tabs = st.tabs(["Overview", "Credential guardrail", "Swap decision", "Manager queue"])

with tabs[0]:
    expired_count = sum(e["expiry"] < today for e in employees)
    a,b,c,d = st.columns(4)
    a.metric("Pending requests", "12", help="Illustrative demo value")
    b.metric("Expired credentials", expired_count)
    c.metric("Eligible swaps", "8", help="Illustrative demo value")
    d.metric("Exceptions", "3", help="Illustrative demo value")
    st.subheader("Product intent")
    st.markdown("""
    This prototype demonstrates three principles:
    1. **Prevent unsafe assignment:** a required expired credential blocks the assignment.
    2. **Make swap decisions consistently:** check training, credential status and projected weekly hours.
    3. **Escalate exceptions:** route cases that fail a rule to a manager rather than auto-approving them.
    """)
    st.info("The brief estimates certificate expiry blocking at approximately one sprint. The effort for a reusable rules engine is unknown and must be estimated by Engineering.")

with tabs[1]:
    st.subheader("Employee credential register")
    st.caption("All names and dates below are fictional sample records.")
    for e in employees:
        days_left = (e["expiry"] - today).days
        if days_left < 0:
            status = "BLOCK — expired"
        elif days_left <= warning_days:
            status = f"Expiring soon — {days_left} days"
        else:
            status = "Valid"
        with st.container(border=True):
            c1,c2,c3,c4 = st.columns([2,1,1,2])
            c1.markdown(f"**{e['name']}**  \n{e['role']}")
            c2.write(e["credential"])
            c3.write(e["expiry"].strftime("%d %b %Y"))
            c4.write(status)
    st.subheader("Test a proposed assignment")
    employee_name = st.selectbox("Employee", [e["name"] for e in employees])
    employee = next(e for e in employees if e["name"] == employee_name)
    credential_required = st.checkbox("This shift requires the listed credential", value=(employee["role"] == "Nurse"))
    if st.button("Check assignment", type="primary", key="check_assignment"):
        if credential_required and employee["expiry"] < today:
            st.error(f"BLOCKED: {employee['credential']} expired on {employee['expiry']:%d %b %Y}. Do not assign this employee to the shift.")
        else:
            st.success("No credential-expiry block triggered by the selected demo rule. Other scheduling and policy checks are still required.")

with tabs[2]:
    st.subheader("Evaluate a shift swap")
    left, right = st.columns(2)
    with left:
        requester = st.selectbox("Requesting employee", [e["name"] for e in employees], index=1)
        recipient = st.selectbox("Employee taking the shift", [e["name"] for e in employees], index=2)
        trained = st.checkbox("Recipient is trained for the role/station", value=True)
        requires_credential = st.checkbox("Shift requires a current credential", value=False)
        credential_current = st.checkbox("Recipient's required credential is current", value=True)
    with right:
        current_hours = st.number_input("Recipient's current scheduled hours", min_value=0, max_value=100, value=40)
        added_hours = st.number_input("Hours added by the swap", min_value=0, max_value=24, value=8)
        projected = current_hours + added_hours
        st.metric("Projected weekly hours", f"{projected} hrs", f"{projected-weekly_limit:+} vs threshold")
    if st.button("Evaluate swap", type="primary"):
        reasons = []
        if not trained:
            reasons.append("Role/station training is not confirmed.")
        if requires_credential and not credential_current:
            reasons.append("Required credential is not confirmed as current.")
        if projected > weekly_limit:
            reasons.append(f"Projected hours exceed {weekly_limit}; approval is required.")
        if reasons:
            st.warning("DO NOT AUTO-APPROVE")
            for reason in reasons:
                st.write(f"• {reason}")
            st.write("Recommended outcome: block the assignment if a mandatory credential has expired; otherwise route the exception to the configured manager.")
        elif auto_approve:
            st.success("ELIGIBLE FOR AUTOMATIC APPROVAL under the demo rules.")
            st.write(f"Illustrative decision for {requester} → {recipient}. A production system must record the reason and notify affected employees.")
        else:
            st.info("Rules passed, but automatic approval is disabled. Route the request to a manager.")

with tabs[3]:
    st.subheader("Illustrative manager queue")
    queue = [
        ("SW-1042", "Meera Shah → Ravi Kumar", "Rules passed", "Eligible for auto-approval"),
        ("SW-1043", "Ananya Rao → Meera Shah", "Credential expired", "Blocked"),
        ("SW-1044", "Ravi Kumar → Kiran Das", "Projected 52 hours/week", "Regional approval required"),
    ]
    for request_id, people, reason, status in queue:
        with st.container(border=True):
            x,y,z = st.columns([1,2,2])
            x.markdown(f"**{request_id}**")
            y.write(people)
            z.write(status)
            st.caption(reason)

st.divider()
st.caption("Prototype limitations: simulated data; no authentication, database, audit trail, notifications, integrations or production policy engine. Never use this demo for real scheduling or compliance decisions.")
