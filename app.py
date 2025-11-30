# contents of file
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import calendar
import math

# --- CONFIGURATION & STATE INITIALIZATION ---
st.set_page_config(page_title="VOLTAS CR Plant", layout="wide")

# Header
st.title("VOLTAS CR Plant")
st.markdown("<h4 style='font-size: 14px; margin-top: -15px;'>Waghodia</h4>", unsafe_allow_html=True)
st.markdown("---")

# --- SESSION STATE INITIALIZATION ---
if 'production_data' not in st.session_state:
    st.session_state.production_data = []

# Two main product categories (top-level)
if 'categories' not in st.session_state:
    st.session_state.categories = ["Chest Freezer", "Water Dispenser"]

# Models for Chest Freezer assembly flow (used in Pre-assembly, Cabinet Foaming, Door Foaming, CF Final Line)
if 'cf_models' not in st.session_state:
    st.session_state.cf_models = ["CF-Model-100", "CF-Model-200"]

# Models for Water Dispenser (independent)
if 'wd_models' not in st.session_state:
    st.session_state.wd_models = ["WD-Model-A", "WD-Model-B"]

# CRF (parts) are separate — they produce parts required by CF assembly. CRF has its own models/categories.
if 'crf_models' not in st.session_state:
    st.session_state.crf_models = ["CRF-Part-A", "CRF-Part-B"]
if 'crf_categories' not in st.session_state:
    st.session_state.crf_categories = ["CRF Parts"]

# activation flags for models (works across all model sets)
if 'active_models' not in st.session_state:
    st.session_state.active_models = {}
    for m in st.session_state.crf_models + st.session_state.cf_models + st.session_state.wd_models:
        st.session_state.active_models[m] = True

# plan_data default storage (backwards-compatible)
if 'plan_data' not in st.session_state:
    st.session_state.plan_data = {}
    # Initialize for all known models
    for m in st.session_state.crf_models + st.session_state.cf_models + st.session_state.wd_models:
        st.session_state.plan_data.setdefault(m, {'monthly': 0, 'daily': 0})

# monthly/daily plans keyed by YYYY-MM and YYYY-MM-DD
if 'monthly_plans' not in st.session_state:
    st.session_state.monthly_plans = {}
if 'daily_plans' not in st.session_state:
    st.session_state.daily_plans = {}

# CF Area configuration (explicit)
CF_AREAS = ["CRF", "Pre-Assembly", "Cabinet Foaming", "Door Foaming", "CF Final Line"]
WD_AREAS = ["WD Final Line"]
ALL_AREAS = CF_AREAS + WD_AREAS

# --- NAVIGATION ---
menu = st.radio("Select Module:", 
    ["1. Plan Entry", "2. Production Entry", "3. Plan Vs Actual Report", "4. Settings"], 
    horizontal=True)
st.markdown("---")

# --- SETTINGS ---
if menu == "4. Settings":
    st.header("⚙️ Settings")
    st.info("Manage categories and models. CRF (parts) has its own categories/models. CF assembly uses cf_models. WD uses wd_models.")

    tab_cat, tab_model, tab_crf = st.tabs(["Manage Top Categories", "Manage Models (CF/WD)", "Manage CRF Models/Categories"])

    with tab_cat:
        st.subheader("Top-level Product Categories")
        st.write("Current:", st.session_state.categories)
        new_cat = st.text_input("New Top Category (Chest Freezer / Water Dispenser)", key="new_top_cat")
        if st.button("Add Top Category"):
            if new_cat and new_cat not in st.session_state.categories:
                st.session_state.categories.append(new_cat)
                st.success(f"Added top category: {new_cat}")
            elif new_cat:
                st.warning("Category already exists")
    with tab_model:
        st.subheader("Add CF / WD Models")
        col1, col2 = st.columns(2)
        with col1:
            sel = st.selectbox("Choose Product Line to add model to", ["Chest Freezer", "Water Dispenser"], key="add_model_line")
            new_model = st.text_input("New Model Name (e.g. CF-Model-300 / WD-Model-C)", key="new_model_name")
            if st.button("Add Model"):
                if new_model:
                    if sel == "Chest Freezer":
                        if new_model not in st.session_state.cf_models:
                            st.session_state.cf_models.append(new_model)
                            st.session_state.active_models[new_model] = True
                            st.session_state.plan_data[new_model] = {'monthly': 0, 'daily': 0}
                            st.success(f"Added CF model {new_model}")
                        else:
                            st.warning("Model exists")
                    else:
                        if new_model not in st.session_state.wd_models:
                            st.session_state.wd_models.append(new_model)
                            st.session_state.active_models[new_model] = True
                            st.session_state.plan_data[new_model] = {'monthly': 0, 'daily': 0}
                            st.success(f"Added WD model {new_model}")
                        else:
                            st.warning("Model exists")
        with col2:
            st.subheader("Activate/Deactivate Models (all)")
            for model in sorted(set(st.session_state.crf_models + st.session_state.cf_models + st.session_state.wd_models)):
                is_active = st.checkbox(model, value=st.session_state.active_models.get(model, True), key=f"act_{model}")
                st.session_state.active_models[model] = is_active

    with tab_crf:
        st.subheader("Manage CRF (Parts) Models & Categories")
        st.write("CRF Categories:", st.session_state.crf_categories)
        new_crf_cat = st.text_input("New CRF Category Name", key="new_crf_cat")
        if st.button("Add CRF Category"):
            if new_crf_cat and new_crf_cat not in st.session_state.crf_categories:
                st.session_state.crf_categories.append(new_crf_cat)
                st.success(f"Added CRF category {new_crf_cat}")
            elif new_crf_cat:
                st.warning("CRF category exists")
        st.markdown("---")
        st.write("CRF Models:", st.session_state.crf_models)
        new_crf_model = st.text_input("New CRF Model Name", key="new_crf_model")
        if st.button("Add CRF Model"):
            if new_crf_model and new_crf_model not in st.session_state.crf_models:
                st.session_state.crf_models.append(new_crf_model)
                st.session_state.active_models[new_crf_model] = True
                st.session_state.plan_data[new_crf_model] = {'monthly': 0, 'daily': 0}
                st.success(f"Added CRF model {new_crf_model}")
            elif new_crf_model:
                st.warning("CRF model exists")

# --- PLAN ENTRY ---
elif menu == "1. Plan Entry":
    st.header("🗓️ Production Plan Entry (password protected)")
    password = st.text_input("Enter Plan Password", type="password")
    if password == "admin":
        st.success("Access Granted")
        tab_monthly, tab_daily = st.tabs(["Monthly Plan", "Daily Plan"])

        active_models_list = [m for m in st.session_state.cf_models + st.session_state.wd_models + st.session_state.crf_models if st.session_state.active_models.get(m, True)]

        with tab_monthly:
            st.subheader("Set Monthly Production Targets (per model)")
            with st.form("monthly_plan_form"):
                month_sel = st.date_input("Select Month", datetime.now().date(), key="monthly_plan_month_picker")
                month_str = month_sel.strftime("%Y-%m")
                monthly_entries = {}
                for model in active_models_list:
                    default = st.session_state.monthly_plans.get(month_str, {}).get(model, st.session_state.plan_data.get(model, {}).get('monthly', 0))
                    monthly_entries[model] = st.number_input(f"Monthly Target for {model}", min_value=0, value=int(default), key=f"mon_{model}")
                if st.form_submit_button("Save Monthly Plan"):
                    for model, qty in monthly_entries.items():
                        st.session_state.monthly_plans.setdefault(month_str, {})[model] = int(qty)
                        st.session_state.plan_data.setdefault(model, {'monthly': 0, 'daily': 0})['monthly'] = int(qty)
                    st.success(f"Monthly plan saved for {month_str}")

        with tab_daily:
            st.subheader("Set Daily Production Targets (per model)")
            with st.form("daily_plan_form"):
                date_sel = st.date_input("Select Date", datetime.now().date(), key="daily_plan_date_picker")
                date_str = date_sel.strftime("%Y-%m-%d")
                daily_entries = {}
                for model in active_models_list:
                    default = st.session_state.daily_plans.get(date_str, {}).get(model, st.session_state.plan_data.get(model, {}).get('daily', 0))
                    daily_entries[model] = st.number_input(f"Daily Target for {model}", min_value=0, value=int(default), key=f"day_{model}")
                if st.form_submit_button("Save Daily Plan"):
                    for model, qty in daily_entries.items():
                        st.session_state.daily_plans.setdefault(date_str, {})[model] = int(qty)
                        st.session_state.plan_data.setdefault(model, {'monthly': 0, 'daily': 0})['daily'] = int(qty)
                    st.success(f"Daily plan saved for {date_str}")
    elif password:
        st.error("Incorrect Password")

# --- PRODUCTION ENTRY ---
elif menu == "2. Production Entry":
    st.header("📝 Production Data Entry")
    product_type = st.radio("Select Product Line:", ["❄️ Chest Freezer", "💧 Water Dispenser"], horizontal=True)
    st.markdown("---")

    if product_type == "❄️ Chest Freezer":
        st.subheader("Chest Freezer Line Entry")
        area_tabs = st.tabs(CF_AREAS)
        for i, area in enumerate(CF_AREAS):
            with area_tabs[i]:
                st.markdown(f"#### {area} Production Log")
                with st.form(f"form_{area}"):
                    supervisor_name = st.text_input("Supervisor Name (Required)", key=f"sup_{area}")
                    if f'temp_entries_{area}' not in st.session_state:
                        st.session_state[f'temp_entries_{area}'] = []
                    st.markdown("---")

                    # CRF is special: allow selecting CRF category & CRF model (parts)
                    if area == "CRF":
                        col1, col2 = st.columns(2)
                        with col1:
                            crf_cat = st.selectbox("CRF Category", st.session_state.crf_categories, key=f"crf_cat_{area}")
                        with col2:
                            crf_available_models = [m for m in st.session_state.crf_models if st.session_state.active_models.get(m, True)]
                            crf_model = st.selectbox("CRF Model (Part)", crf_available_models, key=f"crf_model_{area}")
                        production_qty = st.number_input("Production Entry Field", min_value=1, value=1, key=f"qty_{area}")
                        if st.form_submit_button("Add to List"):
                            if supervisor_name and crf_model:
                                entry = {
                                    "Supervisor": supervisor_name,
                                    "Category": crf_cat,
                                    "Model": crf_model,
                                    "Quantity": production_qty
                                }
                                st.session_state[f'temp_entries_{area}'].append(entry)
                                st.success(f"Added {production_qty} units of {crf_model} to list.")
                            else:
                                st.error("Provide Supervisor and select CRF model.")
                    else:
                        # Assembly areas: single CF assembly line category ("Chest Freezer") and CF models
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Category:** Chest Freezer (Assembly)")
                        with col2:
                            cf_available_models = [m for m in st.session_state.cf_models if st.session_state.active_models.get(m, True)]
                            model = st.selectbox("Model", cf_available_models, key=f"model_{area}")
                        production_qty = st.number_input("Production Entry Field", min_value=1, value=1, key=f"qty_{area}")
                        if st.form_submit_button("Add to List"):
                            if supervisor_name and model:
                                entry = {
                                    "Supervisor": supervisor_name,
                                    "Category": "Chest Freezer",
                                    "Model": model,
                                    "Quantity": production_qty
                                }
                                st.session_state[f'temp_entries_{area}'].append(entry)
                                st.success(f"Added {production_qty} units of {model} to list.")
                            else:
                                st.error("Provide Supervisor and select a model.")

                    st.markdown("---")
                    if st.session_state[f'temp_entries_{area}']:
                        st.markdown("**Pending Submissions:**")
                        st.dataframe(pd.DataFrame(st.session_state[f'temp_entries_{area}']), hide_index=True)
                        if st.form_submit_button("SUBMIT ALL ENTRIES", type="primary"):
                            if st.session_state[f'temp_entries_{area}']:
                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                                for e in st.session_state[f'temp_entries_{area}']:
                                    # For CRF entries we set Product = "CRF_PARTS", for assembly CF product mark "CF"
                                    product_tag = "CRF_PARTS" if area == "CRF" else "CF"
                                    st.session_state.production_data.append({
                                        "Date": timestamp,
                                        "Area": area,
                                        "Supervisor": e['Supervisor'],
                                        "Category": e['Category'],
                                        "Model": e['Model'],
                                        "Actual": e['Quantity'],
                                        "Product": product_tag
                                    })
                                st.session_state[f'temp_entries_{area}'] = []
                                st.success(f"✅ All {area} entries submitted!")
                    else:
                        st.warning("Add entries then submit.")

    else:
        # Water Dispenser flow
        st.subheader("Water Dispenser Line Entry")
        area = WD_AREAS[0]
        st.markdown(f"#### {area} Production Log")
        with st.form(f"form_{area}"):
            supervisor_name = st.text_input("Supervisor Name (Required)", key=f"sup_{area}")
            if f'temp_entries_{area}' not in st.session_state:
                st.session_state[f'temp_entries_{area}'] = []
            st.markdown("---")
            wd_available_models = [m for m in st.session_state.wd_models if st.session_state.active_models.get(m, True)]
            model = st.selectbox("Model", wd_available_models, key=f"model_{area}")
            production_qty = st.number_input("Production Entry Field", min_value=1, value=1, key=f"qty_{area}")
            if st.form_submit_button("Add to List"):
                if supervisor_name and model:
                    entry = {
                        "Supervisor": supervisor_name,
                        "Category": "Water Dispenser",
                        "Model": model,
                        "Quantity": production_qty
                    }
                    st.session_state[f'temp_entries_{area}'].append(entry)
                    st.success(f"Added {production_qty} units of {model} to list.")
                else:
                    st.error("Provide Supervisor and select a model.")
            st.markdown("---")
            if st.session_state[f'temp_entries_{area}']:
                st.dataframe(pd.DataFrame(st.session_state[f'temp_entries_{area}']), hide_index=True)
                if st.form_submit_button("SUBMIT ALL ENTRIES", type="primary"):
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    for e in st.session_state[f'temp_entries_{area}']:
                        st.session_state.production_data.append({
                            "Date": timestamp,
                            "Area": area,
                            "Supervisor": e['Supervisor'],
                            "Category": e['Category'],
                            "Model": e['Model'],
                            "Actual": e['Quantity'],
                            "Product": "WD"
                        })
                    st.session_state[f'temp_entries_{area}'] = []
                    st.success("✅ All entries submitted!")

# --- REPORTING ---
elif menu == "3. Plan Vs Actual Report":
    st.header("📊 Production Reports")
    tab_wip, tab_daily, tab_monthly = st.tabs(["WIP Status", "Daily Achievement", "Monthly Report"])

    # --- WIP STATUS with divisions mapped correctly ---
    with tab_wip:
        st.subheader("WIP Status - Divisions")
        st.info("Divisions: CRF (parts) | CF Assembly (Pre-assembly → ... → CF Final Line) | WD (independent)")
        division = st.selectbox("Select Division", ["CRF Division", "CF Assembly Division", "WD Division"], key="wip_div_select")
        wip_date = st.date_input("Select Date for WIP", datetime.now().date(), key="wip_date")
        date_str = wip_date.strftime("%Y-%m-%d")
        month_str = wip_date.strftime("%Y-%m")
        days_in_month = calendar.monthrange(wip_date.year, wip_date.month)[1]

        prod_df = pd.DataFrame(st.session_state.production_data)
        if prod_df.empty:
            st.info("No production data yet.")
        else:
            prod_df['Report_Date'] = pd.to_datetime(prod_df['Date']).dt.strftime("%Y-%m-%d")

            if division == "CRF Division":
                display_areas = ["CRF"]
                models_in_div = [m for m in st.session_state.crf_models if st.session_state.active_models.get(m, True)]
            elif division == "WD Division":
                display_areas = ["WD Final Line"]
                models_in_div = [m for m in st.session_state.wd_models if st.session_state.active_models.get(m, True)]
            else:
                # CF Assembly division (Pre-Assembly, Cabinet Foaming, Door Foaming, CF Final Line)
                display_areas = ["Pre-Assembly", "Cabinet Foaming", "Door Foaming", "CF Final Line"]
                models_in_div = [m for m in st.session_state.cf_models if st.session_state.active_models.get(m, True)]

            # Filter production entries for the chosen date and relevant areas
            filtered = prod_df[(prod_df['Report_Date'] == date_str) & (prod_df['Area'].isin(display_areas))]

            if filtered.empty:
                st.info("No production data for selected division/date.")
            else:
                # monthly plans for the month (we use monthly plan as 'Plan (Monthly)' column)
                monthly_plans_for_month = st.session_state.monthly_plans.get(month_str, {})

                area_plan = {}
                area_actual = {}
                for area in display_areas:
                    plan_values = []
                    for model in models_in_div:
                        mon_val = monthly_plans_for_month.get(model, None)
                        if mon_val is None:
                            mon_val = st.session_state.plan_data.get(model, {}).get('monthly', None)
                        if mon_val is None:
                            plan_values.append(np.nan)
                        else:
                            try:
                                plan_values.append(float(mon_val))
                            except Exception:
                                plan_values.append(np.nan)
                    if len(plan_values) == 0 or np.all(np.isnan(plan_values)):
                        area_plan[area] = np.nan
                    else:
                        area_plan[area] = float(np.nansum(plan_values))
                    area_actual[area] = int(filtered[filtered['Area'] == area]['Actual'].sum())

                # Build rows: For CF Assembly show WIP between sequential areas; for CRF/WD just show area rows
                rows = []
                if division in ("CRF Division", "WD Division"):
                    for area in display_areas:
                        rows.append([area, area_plan.get(area, np.nan), area_actual.get(area, 0)])
                else:
                    seq = display_areas
                    rows.append([seq[0], area_plan.get(seq[0], np.nan), area_actual.get(seq[0], 0)])
                    for i in range(len(seq) - 1):
                        a_from = seq[i]
                        a_to = seq[i + 1]
                        plan_wip = (0.0 if pd.isna(area_plan.get(a_from)) else area_plan.get(a_from)) - (0.0 if pd.isna(area_plan.get(a_to)) else area_plan.get(a_to))
                        act_wip = area_actual.get(a_from, 0) - area_actual.get(a_to, 0)
                        rows.append([f"WIP ({a_from} → {a_to})", plan_wip, act_wip])
                        # next iteration will append next area except last
                    rows.append([seq[-1], area_plan.get(seq[-1], np.nan), area_actual.get(seq[-1], 0)])

                wip_grid = pd.DataFrame(rows, columns=["Production Area", "Plan (Monthly)", "Act (Day)"])

                # Styling function
                def style_row_wip(row):
                    styles = []
                    plan = row["Plan (Monthly)"]
                    act = row["Act (Day)"]
                    styles.append("font-weight: bold;")
                    if pd.isna(plan):
                        styles.append("background-color: #f0f0f0; color: #6c757d;")
                    else:
                        styles.append("background-color: #e7f3ff; color: #0b5394; font-weight: 600;")
                    # color Act relative to per-day equivalent where plan exists
                    if not pd.isna(plan) and plan > 0:
                        per_day = plan / days_in_month if days_in_month > 0 else 0
                        if per_day > 0 and act >= per_day:
                            styles.append("background-color: #d4edda; color: #155724; font-weight: 600;")
                        elif act == 0:
                            styles.append("background-color: #f0f0f0; color: #6c757d;")
                        else:
                            styles.append("background-color: #fff3cd; color: #856404;")
                    else:
                        styles.append("background-color: #f0f0f0; color: #6c757d;")
                    return styles

                styled = wip_grid.style.apply(style_row_wip, axis=1)

                def fmt_plan(x):
                    return "N/A" if pd.isna(x) else f"{int(round(x))}"
                def fmt_act(x):
                    return f"{int(x)}"

                styled = styled.format({
                    "Plan (Monthly)": fmt_plan,
                    "Act (Day)": fmt_act
                })

                st.markdown(f"### WIP Grid — {division} on {date_str}")
                st.dataframe(styled, hide_index=True)

    # --- DAILY ACHIEVEMENT ---
    with tab_daily:
        st.subheader("Daily Achievement Report")
        report_date = st.date_input("Select Date", datetime.now().date(), key="daily_report_date")
        date_str = report_date.strftime("%Y-%m-%d")
        area_filter = st.selectbox("Select Area", ["All"] + ALL_AREAS, key="daily_area_filter")
        daily_df = pd.DataFrame(st.session_state.production_data)
        if not daily_df.empty:
            daily_df['Report_Date'] = pd.to_datetime(daily_df['Date']).dt.strftime("%Y-%m-%d")
            filtered_df = daily_df[daily_df['Report_Date'] == date_str]
            if area_filter != "All":
                filtered_df = filtered_df[filtered_df['Area'] == area_filter]

            if not filtered_df.empty:
                model_summary = filtered_df.groupby(['Model', 'Area'])['Actual'].sum().reset_index()
                model_summary.rename(columns={'Actual': 'Act'}, inplace=True)
                daily_plan_for_date = st.session_state.daily_plans.get(date_str, {})

                def get_model_plan(model):
                    if model in daily_plan_for_date:
                        try:
                            return int(daily_plan_for_date.get(model, 0))
                        except Exception:
                            return np.nan
                    return np.nan

                model_summary['Plan'] = model_summary['Model'].apply(get_model_plan)

                def compute_ach(row):
                    plan = row['Plan']
                    act = row['Act']
                    if pd.isna(plan):
                        return np.nan
                    if plan == 0:
                        return 0.0 if act == 0 else 100.0
                    return (act / plan) * 100.0

                model_summary['Achievement %'] = model_summary.apply(compute_ach, axis=1)
                model_summary["Act"] = pd.to_numeric(model_summary["Act"], errors="coerce").fillna(0).astype(int)
                model_summary["Achievement %"] = pd.to_numeric(model_summary["Achievement %"], errors="coerce")

                # Styling for daily table
                def style_daily_row(row):
                    styles = []
                    styles.append("font-weight: bold;")
                    styles.append("background-color: #f8f9fa; color: #333333;")
                    plan = row["Plan"]
                    act = row["Act"]
                    if not pd.isna(plan) and plan > 0:
                        if act >= plan:
                            styles.append("background-color: #d4edda; color: #155724; font-weight: 600;")
                        elif act == 0:
                            styles.append("background-color: #f0f0f0; color: #6c757d;")
                        else:
                            styles.append("background-color: #fff3cd; color: #856404;")
                    else:
                        styles.append("background-color: #f0f0f0; color: #6c757d;")
                    if pd.isna(plan):
                        styles.append("background-color: #f0f0f0; color: #6c757d;")
                    else:
                        styles.append("background-color: #e7f3ff; color: #0b5394; font-weight: 600;")
                    ach = row["Achievement %"]
                    if pd.isna(ach):
                        styles.append("background-color: #f0f0f0; color: #6c757d;")
                    else:
                        try:
                            val = float(ach)
                        except Exception:
                            val = 0.0
                        if val >= 100:
                            styles.append("background-color: #d4edda; color: #155724; font-weight: 700;")
                        elif val >= 90:
                            styles.append("background-color: #e2f0d9; color: #155724;")
                        elif val >= 75:
                            styles.append("background-color: #fff3cd; color: #856404;")
                        else:
                            styles.append("background-color: #f8d7da; color: #721c24;")
                    return styles

                styled_daily = model_summary.style.apply(style_daily_row, axis=1)

                def fmt_plan(x):
                    return "N/A" if pd.isna(x) else f"{int(x)}"
                def fmt_ach(x):
                    return "N/A" if pd.isna(x) else f"{x:.1f}%"

                styled_daily = styled_daily.format({
                    "Plan": fmt_plan,
                    "Act": "{:d}",
                    "Achievement %": fmt_ach
                })

                st.markdown(f"### Daily Production for {date_str} (Area: {area_filter})")
                st.dataframe(styled_daily, hide_index=True)

                st.markdown("#### Total Actual by Model")
                graph_data = model_summary.groupby('Model')['Act'].sum()
                st.bar_chart(graph_data)
            else:
                st.info("No production data found for this date/area.")
        else:
            st.info("No production data entered yet.")

    # --- MONTHLY REPORT ---
    with tab_monthly:
        st.subheader("Monthly Report (Plan vs Actual)")
        month_filter = st.date_input("Select Month (pick any date in month)", datetime.now().date(), key="monthly_date_report")
        month_str = month_filter.strftime("%Y-%m")
        area_filter_month = st.selectbox("Select Area", ["All"] + ALL_AREAS, key="monthly_area_filter")

        monthly_df = pd.DataFrame(st.session_state.production_data)
        if not monthly_df.empty:
            monthly_df['Report_Month'] = pd.to_datetime(monthly_df['Date']).dt.strftime("%Y-%m")
            monthly_filtered = monthly_df[monthly_df['Report_Month'] == month_str]
            if area_filter_month != "All":
                monthly_filtered = monthly_filtered[monthly_filtered['Area'] == area_filter_month]

            if not monthly_filtered.empty:
                report_data = []
                monthly_plans_for_month = st.session_state.monthly_plans.get(month_str, {})

                # iterate all known models (CRF/CF/WD)
                all_models = sorted(set(list(st.session_state.crf_models) + list(st.session_state.cf_models) + list(st.session_state.wd_models)))
                for model in all_models:
                    plan_qty = monthly_plans_for_month.get(model, st.session_state.plan_data.get(model, {}).get('monthly', 0))

                    # prefer final-line actuals by product type
                    if model in st.session_state.wd_models:
                        actuals_final = monthly_filtered[(monthly_filtered['Model'] == model) & (monthly_filtered['Area'] == 'WD Final Line')]['Actual'].sum()
                    elif model in st.session_state.cf_models:
                        actuals_final = monthly_filtered[(monthly_filtered['Model'] == model) & (monthly_filtered['Area'] == 'CF Final Line')]['Actual'].sum()
                    elif model in st.session_state.crf_models:
                        # CRF part models: only CRF area entries matter
                        actuals_final = monthly_filtered[(monthly_filtered['Model'] == model) & (monthly_filtered['Area'] == 'CRF')]['Actual'].sum()
                    else:
                        actuals_final = 0

                    if actuals_final == 0:
                        # fallback to sum across all areas for that model
                        actuals = monthly_filtered[monthly_filtered['Model'] == model]['Actual'].sum()
                    else:
                        actuals = actuals_final

                    try:
                        actuals = int(actuals)
                    except Exception:
                        actuals = int(actuals or 0)

                    report_data.append({
                        "Model": model,
                        "Category": monthly_filtered[monthly_filtered['Model'] == model]['Category'].iloc[0] if not monthly_filtered[monthly_filtered['Model'] == model].empty else "N/A",
                        "Planned Qty": int(plan_qty or 0),
                        "Actual Qty": actuals,
                        "Variance": actuals - int(plan_qty or 0)
                    })

                report_df = pd.DataFrame(report_data)
                report_df = report_df[(report_df['Planned Qty'] != 0) | (report_df['Actual Qty'] != 0)]

                st.dataframe(report_df.style.applymap(lambda x: 'color: red' if x < 0 else 'color: green', subset=['Variance']))
                st.bar_chart(report_df.set_index('Model')[['Planned Qty', 'Actual Qty']])
            else:
                st.info("No production data found for this month/area.")
        else:
            st.info("No production data entered yet.")
