import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION & STATE INITIALIZATION ---
st.set_page_config(page_title="Production Planner", layout="wide")

# Initialize Session State to store data (Simulating a Database)
if 'wd_plan' not in st.session_state:
    st.session_state.wd_plan = {'WD-Model-A': 0, 'WD-Model-B': 0, 'WD-Model-C': 0}
if 'cf_plan' not in st.session_state:
    st.session_state.cf_plan = {'CF-Small-100': 0, 'CF-Med-200': 0, 'CF-Large-300': 0}
if 'production_data' not in st.session_state:
    st.session_state.production_data = [] # List to store log entries
if 'active_models' not in st.session_state:
    st.session_state.active_models = {
        'WD-Model-A': True, 'WD-Model-B': True, 'WD-Model-C': True,
        'CF-Small-100': True, 'CF-Med-200': True, 'CF-Large-300': True
    }

# --- NAVIGATION (TOP ICONS SIMULATION) ---
st.title("🏭 Production Planning & Entry App")
menu = st.radio("Select Module:", 
    ["Modelwise Plan (Monthly/Daily)", "Areawise Daily Production", "Plan Vs Actual Report"], 
    horizontal=True)

st.markdown("---")

# --- MODULE 1: PLANNING (PASSWORD PROTECTED) ---
if menu == "Modelwise Plan (Monthly/Daily)":
    st.subheader("🔐 Restricted Access: Planning Department")
    password = st.text_input("Enter Password", type="password")

    if password == "admin": # Simple password for prototype
        plan_type = st.selectbox("Select Plan Type", ["Monthly Plan", "Daily Plan"])

        tab1, tab2 = st.tabs(["💧 Water Dispenser (WD)", "❄️ Chest Freezer (CF)"])

        with tab1:
            st.info("Set Targets for Water Dispensers")
            for model in st.session_state.wd_plan.keys():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{model}**")
                with col2:
                    val = st.number_input(f"Plan Qty for {model}", min_value=0, value=st.session_state.wd_plan[model], key=f"p_{model}")
                    st.session_state.wd_plan[model] = val
                with col3:
                    is_active = st.checkbox("Active", value=st.session_state.active_models[model], key=f"act_{model}")
                    st.session_state.active_models[model] = is_active
            st.success(f"{plan_type} for WD Updated!")

        with tab2:
            st.info("Set Targets for Chest Freezers (Final Line)")
            for model in st.session_state.cf_plan.keys():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{model}**")
                with col2:
                    val = st.number_input(f"Plan Qty for {model}", min_value=0, value=st.session_state.cf_plan[model], key=f"p_{model}")
                    st.session_state.cf_plan[model] = val
                with col3:
                    is_active = st.checkbox("Active", value=st.session_state.active_models[model], key=f"act_{model}")
                    st.session_state.active_models[model] = is_active
            st.success(f"{plan_type} for CF Updated!")

    elif password:
        st.error("Incorrect Password")

# --- MODULE 2: DAILY PRODUCTION ENTRY ---
elif menu == "Areawise Daily Production":
    st.subheader("📝 Production Floor Entry")

    prod_type = st.selectbox("Select Product Line", ["Water Dispenser", "Chest Freezer"])

    # === WATER DISPENSER FLOW ===
    if prod_type == "Water Dispenser":
        st.markdown("### 💧 WD Assembly Line")

        supervisor_name = st.text_input("Supervisor Name (Required)")

        # Display Grid for Entry
        st.write("Enter Production Quantities:")

        # Filter only Active Models
        active_wd = [m for m in st.session_state.wd_plan if st.session_state.active_models[m]]

        input_data = {}
        has_entry = False

        with st.form("wd_entry_form"):
            for model in active_wd:
                c1, c2, c3 = st.columns(3)
                c1.write(model)
                c1.caption(f"Plan: {st.session_state.wd_plan[model]}")
                qty = c2.number_input(f"Actual Qty {model}", min_value=0, key=f"entry_{model}")
                input_data[model] = qty
                if qty > 0:
                    has_entry = True

            # Save Logic
            submitted = st.form_submit_button("Save Production Data")

            if submitted:
                if not supervisor_name:
                    st.error("⚠️ Supervisor Name is required!")
                elif not has_entry:
                    st.error("⚠️ Enter at least one quantity greater than 0.")
                else:
                    # Save to dummy database
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    for m, q in input_data.items():
                        if q > 0:
                            st.session_state.production_data.append({
                                "Date": timestamp,
                                "Product": "WD",
                                "Area": "Assembly",
                                "Model": m,
                                "Actual": q,
                                "Supervisor": supervisor_name
                            })
                    st.success("✅ Data Saved Successfully!")

    # === CHEST FREEZER FLOW ===
    elif prod_type == "Chest Freezer":
        st.markdown("### ❄️ Chest Freezer Areas")

        # The 5 Icons/Areas
        area = st.selectbox("Select Area Station", 
                            ["1. CRF (Independent)", 
                             "2. Door Foaming (Independent)", 
                             "3. Pre-assembly (Line Start)", 
                             "4. Cabinet Foaming (Line Mid)", 
                             "5. Final Line (Line End)"])

        st.info(f"You are entering data for: **{area}**")
        supervisor_name = st.text_input("Supervisor/Operator Name")

        # Tabs for Category (Models vs Machines - simulated here as categories)
        tab_models, tab_machines = st.tabs(["By Models", "By Machines"])

        with tab_models:
            # Filter Active CF Models
            active_cf = [m for m in st.session_state.cf_plan if st.session_state.active_models[m]]

            input_cf_data = {}
            has_cf_entry = False

            with st.form("cf_entry_form"):
                for model in active_cf:
                    c1, c2 = st.columns([2,1])
                    c1.write(model)
                    # Only show Plan if it is Final Line
                    if "Final Line" in area:
                        c1.caption(f"Daily Plan: {st.session_state.cf_plan[model]}")

                    qty = c2.number_input(f"Qty {model}", min_value=0, key=f"cf_entry_{model}")
                    input_cf_data[model] = qty
                    if qty > 0:
                        has_cf_entry = True

                submitted_cf = st.form_submit_button("Save Area Data")

                if submitted_cf:
                    if not has_cf_entry:
                         st.error("⚠️ Enter at least one quantity.")
                    else:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                        for m, q in input_cf_data.items():
                            if q > 0:
                                st.session_state.production_data.append({
                                    "Date": timestamp,
                                    "Product": "CF",
                                    "Area": area,
                                    "Model": m,
                                    "Actual": q,
                                    "Supervisor": supervisor_name
                                })
                        st.success(f"✅ Production logged for {area}!")

# --- MODULE 3: REPORTS ---
elif menu == "Plan Vs Actual Report":
    st.subheader("📊 Plan Vs Actual Report")

    if not st.session_state.production_data:
        st.warning("No production data entered yet.")
    else:
        df = pd.DataFrame(st.session_state.production_data)

        # Summary View
        report_view = st.selectbox("View By", ["Weekly", "Daily"])

        st.markdown("### Production Log")
        st.dataframe(df)

        # Simple Pivot Table Logic
        st.markdown("### Summary vs Plan")

        # Aggregate Actuals by Model
        actuals = df.groupby("Model")["Actual"].sum()

        # Combine with Plans
        report_data = []

        # Process WD
        for m, plan in st.session_state.wd_plan.items():
            act = actuals.get(m, 0)
            report_data.append({"Model": m, "Plan": plan, "Actual": act, "Variance": act - plan})

        # Process CF
        for m, plan in st.session_state.cf_plan.items():
            # For CF, we usually compare Final Line actuals against Plan
            # Filter df for Final Line only
            cf_final = df[df['Area'].str.contains("Final", na=False)]
            cf_acts = cf_final.groupby("Model")["Actual"].sum()
            act = cf_acts.get(m, 0)

            report_data.append({"Model": m, "Plan": plan, "Actual": act, "Variance": act - plan})

        report_df = pd.DataFrame(report_data)
        st.dataframe(report_df.style.applymap(lambda x: 'color: red' if x < 0 else 'color: green', subset=['Variance']))

        st.bar_chart(report_df.set_index("Model")[["Plan", "Actual"]])
