import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION & STATE INITIALIZATION ---
st.set_page_config(page_title="VOLTAS CR Plant", layout="wide")

# Header Space Reduction
st.title("VOLTAS CR Plant")
st.markdown("<h4 style='font-size: 14px; margin-top: -15px;'>Waghodia</h4>", unsafe_allow_html=True)
st.markdown("---")

# Initializing Session State
if 'production_data' not in st.session_state:
    st.session_state.production_data = []

# Dynamic Categories and Models
if 'categories' not in st.session_state:
    st.session_state.categories = ["Chest Freezer", "Water Dispenser"]
if 'models' not in st.session_state:
    st.session_state.models = {
        "Chest Freezer": ["CF-Model-100", "CF-Model-200"],
        "Water Dispenser": ["WD-Model-A", "WD-Model-B"]
    }
if 'active_models' not in st.session_state:
    st.session_state.active_models = {
        "CF-Model-100": True, "CF-Model-200": True,
        "WD-Model-A": True, "WD-Model-B": True
    }
# Plan storage: {model_name: {'monthly': qty, 'daily': qty}}
if 'plan_data' not in st.session_state:
    st.session_state.plan_data = {}
    for cat in st.session_state.models:
        for model in st.session_state.models[cat]:
            st.session_state.plan_data[model] = {'monthly': 0, 'daily': 0}

# CF Area Configuration
CF_AREAS = ["CRF", "Pre-Assembly", "Cabinet Foaming", "Door Foaming", "CF Final Line"]
WD_AREAS = ["WD Final Line"]

# --- NAVIGATION ---
menu = st.radio("Select Module:", 
    ["1. Plan Entry", "2. Production Entry", "3. Plan Vs Actual Report", "4. Settings"], 
    horizontal=True)
st.markdown("---")


# --- MODULE 4: SETTINGS (unchanged for now) ---
if menu == "4. Settings":
    st.header("⚙️ Settings: Model & Category Management")
    st.info("Use this area to manage Categories and Models that appear in Production Entry.")
    
    tab_cat, tab_model, tab_activate = st.tabs(["Manage Categories", "Manage Models", "Activate/Deactivate"])

    with tab_cat:
        st.subheader("Add/Rename Categories")
        st.warning("Categories are currently locked to 'Chest Freezer' and 'Water Dispenser' for simplicity.")
        st.write(st.session_state.categories)

    with tab_model:
        st.subheader("Add Models to Category")
        cat_select = st.selectbox("Select Category", st.session_state.categories, key="model_cat_select")
        new_model = st.text_input("New Model Name:")
        if st.button("Add Model") and new_model and cat_select:
            if new_model not in st.session_state.models.get(cat_select, []):
                st.session_state.models[cat_select].append(new_model)
                st.session_state.active_models[new_model] = True
                st.session_state.plan_data[new_model] = {'monthly': 0, 'daily': 0}
                st.success(f"Model '{new_model}' added to {cat_select}.")
            else:
                st.warning("Model already exists.")

    with tab_activate:
        st.subheader("Activate/Deactivate Models")
        for cat in st.session_state.categories:
            st.markdown(f"**{cat}**")
            for model in st.session_state.models.get(cat, []):
                is_active = st.checkbox(model, value=st.session_state.active_models.get(model, True), key=f"active_{model}")
                st.session_state.active_models[model] = is_active
                
# --- MODULE 1: PLAN ENTRY (NEW PASSWORD & DAILY FEATURE) ---
elif menu == "1. Plan Entry":
    st.header("🗓️ Production Plan Entry")
    
    # --- PASSWORD PROTECTION ---
    password = st.text_input("Enter Plan Password", type="password")
    
    if password == "admin": 
        st.success("Access Granted.")
        
        tab_monthly, tab_daily = st.tabs(["Monthly Plan", "Daily Plan"])
        
        active_models_list = [m for cat in st.session_state.models for m in st.session_state.models[cat] if st.session_state.active_models.get(m, True)]
        
        # --- MONTHLY PLAN ---
        with tab_monthly:
            st.subheader("Set Monthly Production Targets")
            monthly_plan_data = {}
            with st.form("monthly_plan_form"):
                for model in active_models_list:
                    default_qty = st.session_state.plan_data.get(model, {}).get('monthly', 0)
                    monthly_plan_data[model] = st.number_input(f"Monthly Target for {model}", min_value=0, value=default_qty, key=f"m_plan_{model}")
                
                if st.form_submit_button("Save Monthly Plan"):
                    for model, qty in monthly_plan_data.items():
                        st.session_state.plan_data[model]['monthly'] = qty
                    st.success("Monthly Plan Saved!")
                    
        # --- DAILY PLAN ---
        with tab_daily:
            st.subheader("Set Daily Production Targets")
            daily_plan_data = {}
            with st.form("daily_plan_form"):
                for model in active_models_list:
                    default_qty = st.session_state.plan_data.get(model, {}).get('daily', 0)
                    daily_plan_data[model] = st.number_input(f"Daily Target for {model}", min_value=0, value=default_qty, key=f"d_plan_{model}")
                
                if st.form_submit_button("Save Daily Plan"):
                    for model, qty in daily_plan_data.items():
                        st.session_state.plan_data[model]['daily'] = qty
                    st.success("Daily Plan Saved!")
                    
    elif password:
        st.error("Incorrect Password")
        

# --- MODULE 2: PRODUCTION ENTRY (NEW NAVIGATION STRUCTURE) ---
elif menu == "2. Production Entry":
    st.header("📝 Production Data Entry")
    
    # --- FIRST SELECTION: PRODUCT TYPE ---
    product_type = st.radio("Select Product Line:", ["❄️ Chest Freezer", "💧 Water Dispenser"], horizontal=True)
    st.markdown("---")

    # --- CF ENTRY ---
    if product_type == "❄️ Chest Freezer":
        st.subheader("Chest Freezer Line Entry")
        
        area_tabs = st.tabs(CF_AREAS)
        
        for i, area in enumerate(CF_AREAS):
            with area_tabs[i]:
                st.markdown(f"#### {area} Production Log")
                
                # --- Single Entry Form ---
                with st.form(f"form_{area}"):
                    supervisor_name = st.text_input("Supervisor Name (Required)", key=f"sup_{area}")
                    
                    if f'temp_entries_{area}' not in st.session_state:
                        st.session_state[f'temp_entries_{area}'] = []
                    
                    st.markdown("---")
                    
                    # 1. CATEGORY & MODEL Selection
                    col1, col2 = st.columns(2)
                    with col1:
                        # Category is fixed to 'Chest Freezer' here
                        st.write("**Category:** Chest Freezer") 
                    
                    available_models = [m for m in st.session_state.models.get("Chest Freezer", []) if st.session_state.active_models.get(m, True)]
                    
                    with col2:
                        model = st.selectbox("Model", available_models, key=f"model_{area}")
                    
                    production_qty = st.number_input("Production Entry Field", min_value=1, value=1, key=f"qty_{area}")
                    
                    # 2. ADD BUTTON for single entry
                    if st.form_submit_button("Add to List"):
                        if supervisor_name and model:
                            entry = {
                                "Supervisor": supervisor_name,
                                "Category": "Chest Freezer",
                                st.success(f"✅ All {area} entries submitted successfully!"):
                            else:
                                st.error("No entries in the list to submit.")
                    else:
                        st.warning("Add entries using the 'Add to List' button before submitting.")
}

    # --- WD ENTRY (Single Tab) ---
    elif product_type == "💧 Water Dispenser":
        st.subheader("Water Dispenser Line Entry")
        area = WD_AREAS[0] # "WD Final Line"
        
        st.markdown(f"#### {area} Production Log")
        
        # --- Single Entry Form ---
        with st.form(f"form_{area}"):
            supervisor_name = st.text_input("Supervisor Name (Required)", key=f"sup_{area}")
            
            if f'temp_entries_{area}' not in st.session_state:
                st.session_state[f'temp_entries_{area}'] = []
            
            st.markdown("---")
            
            # 1. CATEGORY & MODEL Selection
            col1, col2 = st.columns(2)
            with col1:
                # Category is fixed to 'Water Dispenser' here
                st.write("**Category:** Water Dispenser") 
            
            available_models = [m for m in st.session_state.models.get("Water Dispenser", []) if st.session_state.active_models.get(m, True)]
            
            with col2:
                model = st.selectbox("Model", available_models, key=f"model_{area}")
            
            production_qty = st.number_input("Production Entry Field", min_value=1, value=1, key=f"qty_{area}")
            
            # 2. ADD BUTTON for single entry
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
                    st.error("Please enter Supervisor Name and select a Model.")
                    
            st.markdown("---")

            # Display temporary list of entries
            if st.session_state[f'temp_entries_{area}']:
                st.markdown("**Pending Submissions:**")
                temp_df = pd.DataFrame(st.session_state[f'temp_entries_{area}'])
                st.dataframe(temp_df, hide_index=True)
                
                # 3. SUBMIT BUTTON
                if st.form_submit_button("SUBMIT ALL ENTRIES", type="primary"):
                    if st.session_state[f'temp_entries_{area}']:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                        
                        for entry in st.session_state[f'temp_entries_{area}']:
                            st.session_state.production_data.append({
                                "Date": timestamp,
                                "Area": area,
                                "Supervisor": entry['Supervisor'],
                                "Category": entry['Category'],
                                "Model": entry['Model'],
                                "Actual": entry['Quantity'],
                                "Product": "WD"
                            })
                        
                        st.session_state[f'temp_entries_{area}'] = []
                        st.success(f"✅ All {area} entries submitted successfully!")
                    else:
                        st.error("No entries in the list to submit.")
            else:
                st.warning("Add entries using the 'Add to List' button before submitting.")


# --- MODULE 3: REPORTING (Error Fix needed next) ---
elif menu == "3. Plan Vs Actual Report":
    st.header("📊 Production Reports")
    
    tab_wip, tab_daily, tab_monthly = st.tabs(["WIP Status", "Daily Achievement", "Monthly Report"])

    # --- WIP STATUS ---
    with tab_wip:
        st.subheader("Work In Progress (WIP) Status")
        st.warning("WIP tracking requires calculating the difference between sequential area outputs. This logic is complex and will be implemented later.")

    # --- DAILY ACHIEVEMENT ---
    with tab_daily:
        st.subheader("Daily Achievement Report")
        
        report_date = st.date_input("Select Date", datetime.now().date(), key="daily_date")
        
        # FIX FOR REPORT DISPLAY: Ensure correct filtering and grouping
        daily_df = pd.DataFrame(st.session_state.production_data)
        if not daily_df.empty:
            daily_df['Report_Date'] = pd.to_datetime(daily_df['Date']).dt.strftime("%Y-%m-%d")
            filtered_df = daily_df[daily_df['Report_Date'] == report_date.strftime("%Y-%m-%d")]
            
            if not filtered_df.empty:
                # Group by Model and Area for a clear view of daily output across the lines
                model_summary = filtered_df.groupby(['Model', 'Area'])['Actual'].sum().reset_index()
                model_summary.rename(columns={'Actual': 'Total Actual Qty'}, inplace=True)
                st.dataframe(model_summary, hide_index=True)

                st.markdown("#### Daily Production by Model (Total)")
                # Graph total production per model
                graph_data = model_summary.groupby('Model')['Total Actual Qty'].sum()
                st.bar_chart(graph_data)
            else:
                st.info("No production data found for this date.")
        else:
            st.info("No production data entered yet.")

    # --- MONTHLY REPORT (Error Fix needed next) ---
    with tab_monthly:
        st.subheader("Monthly Report (Plan vs Actual)")
        
        month_filter = st.date_input("Select Month", datetime.now().date(), format="MM/YYYY", key="monthly_date")
        month_str = month_filter.strftime("%Y-%m")
        
        monthly_df = pd.DataFrame(st.session_state.production_data)
        if not monthly_df.empty:
            monthly_df['Report_Month'] = pd.to_datetime(monthly_df['Date']).dt.strftime("%Y-%m")
            monthly_filtered = monthly_df[monthly_df['Report_Month'] == month_str]
            
            if not monthly_filtered.empty:
                report_data = []
                
                for model, plan in st.session_state.plan_data.items():
                    plan_qty = plan.get('monthly', 0)
                    
                    # FIX FOR REPORT DISPLAY: Filter Actual based on Final Lines only
                    if model in st.session_state.models['Water Dispenser']:
                        actuals = monthly_filtered[(monthly_filtered['Model'] == model) & (monthly_filtered['Area'] == 'WD Final Line')]['Actual'].sum()
                    elif model in st.session_state.models['Chest Freezer']:
                        actuals = monthly_filtered[(monthly_filtered['Model'] == model) & (monthly_filtered['Area'] == 'CF Final Line')]['Actual'].sum()
                    else:
                         actuals = 0 # Safety catch for unassigned models

                    report_data.append({
                        "Model": model,
                        "Category": monthly_filtered[monthly_filtered['Model'] == model]['Category'].iloc[0] if not monthly_filtered[monthly_filtered['Model'] == model].empty else "N/A",
                        "Planned Qty": plan_qty,
                        "Actual Qty": actuals,
                        "Variance": actuals - plan_qty
                    })

                report_df = pd.DataFrame(report_data)
                
                # Filter out rows where both Planned and Actual are 0 for cleaner report
                report_df = report_df[(report_df['Planned Qty'] != 0) | (report_df['Actual Qty'] != 0)]
                
                st.dataframe(report_df.style.applymap(lambda x: 'color: red' if x < 0 else 'color: green', subset=['Variance']))
                st.bar_chart(report_df.set_index('Model')[['Planned Qty', 'Actual Qty']])
            else:
                st.info("No production data found for this month.")
        else:
            st.info("No production data entered yet.")
