import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION & STATE INITIALIZATION ---
st.set_page_config(page_title="VOLTAS CR Plant", layout="wide")

# Header as requested
st.title("VOLTAS CR Plant")
st.markdown("<h3 style='font-size: 14px;'>Waghodia</h3>", unsafe_allow_html=True)
st.markdown("---")

# Initializing Session State
if 'production_data' not in st.session_state:
    st.session_state.production_data = []

# Dynamic Categories and Models (New Requirement)
if 'categories' not in st.session_state:
    st.session_state.categories = ["Default Category A", "Default Category B"]
if 'models' not in st.session_state:
    st.session_state.models = {
        "Default Category A": ["WD-Model-A", "CF-Model-100"],
        "Default Category B": ["WD-Model-B", "CF-Model-200"]
    }
if 'active_models' not in st.session_state:
    st.session_state.active_models = {
        "WD-Model-A": True, "CF-Model-100": True,
        "WD-Model-B": True, "CF-Model-200": True
    }
if 'monthly_plan' not in st.session_state:
    st.session_state.monthly_plan = {} # Stores plan as {model_name: qty}


# --- NAVIGATION (3 ICONS + Settings Icon) ---
menu = st.radio("Select Module:", 
    ["1. Monthly/Daily Plan", "2. Production Entry", "3. Plan Vs Actual Report", "4. Settings"], 
    horizontal=True)
st.markdown("---")


# --- MODULE 4: SETTINGS (New Feature) ---
if menu == "4. Settings":
    st.header("⚙️ Settings: Model & Category Management")
    st.info("Use this area to manage Categories and Models that appear in Production Entry.")
    
    tab_cat, tab_model, tab_activate = st.tabs(["Manage Categories", "Manage Models", "Activate/Deactivate"])

    with tab_cat:
        st.subheader("Add/Rename Categories")
        new_cat = st.text_input("New Category Name:")
        if st.button("Add New Category") and new_cat and new_cat not in st.session_state.categories:
            st.session_state.categories.append(new_cat)
            st.session_state.models[new_cat] = []
            st.success(f"Category '{new_cat}' added.")
        
        st.markdown("---")
        st.subheader("Current Categories")
        st.write(st.session_state.categories)

    with tab_model:
        st.subheader("Add Models to Category")
        cat_select = st.selectbox("Select Category", st.session_state.categories, key="model_cat_select")
        new_model = st.text_input("New Model Name:")
        if st.button("Add Model") and new_model and cat_select:
            if new_model not in st.session_state.models.get(cat_select, []):
                st.session_state.models[cat_select].append(new_model)
                st.session_state.active_models[new_model] = True
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


# --- MODULE 1: PLAN ENTRY (Placeholder) ---
elif menu == "1. Monthly/Daily Plan":
    st.header("🗓️ Plan Entry")
    st.subheader("Set Monthly Production Targets")
    
    plan_data = {}
    active_models_list = [m for cat in st.session_state.models for m in st.session_state.models[cat] if st.session_state.active_models.get(m, True)]
    
    with st.form("plan_form"):
        st.write("Enter Monthly Plan Quantity for Active Models:")
        for model in active_models_list:
            default_qty = st.session_state.monthly_plan.get(model, 0)
            plan_data[model] = st.number_input(f"Plan for {model}", min_value=0, value=default_qty, key=f"plan_entry_{model}")
        
        if st.form_submit_button("Save Monthly Plan"):
            st.session_state.monthly_plan.update(plan_data)
            st.success("Monthly Plan Saved!")
    st.markdown("---")
    st.info("Daily Plan entry can be added as a separate field or logic here later.")

# --- MODULE 2: PRODUCTION ENTRY ---
elif menu == "2. Production Entry":
    st.header("📝 Production Data Entry")
    
    # --- PRODUCT ICONS ---
    product_type = st.radio("Select Product:", ["❄️ Chest Freezer", "💧 Water Dispenser"], horizontal=True)

    # === CHEST FREEZER ENTRY (New Tab Structure) ===
    if product_type == "❄️ Chest Freezer":
        st.subheader("Chest Freezer Line Entry")
        
        area_tabs = st.tabs(["CRF", "Pre-Assembly", "Cabinet Foaming", "Door Foaming", "CF Final Line"])
        
        for i, area in enumerate(["CRF", "Pre-Assembly", "Cabinet Foaming", "Door Foaming", "CF Final Line"]):
            with area_tabs[i]:
                st.markdown(f"#### {area} Production Log")
                
                # --- Single Entry Form ---
                with st.form(f"form_{area}"):
                    supervisor_name = st.text_input("Supervisor Name (Required)", key=f"sup_{area}")
                    
                    # Store single entries temporarily
                    if f'temp_entries_{area}' not in st.session_state:
                        st.session_state[f'temp_entries_{area}'] = []
                    
                    st.markdown("---")
                    
                    # 1. CATEGORY & MODEL Selection
                    col1, col2 = st.columns(2)
                    with col1:
                        category = st.selectbox("Category", st.session_state.categories, key=f"cat_{area}")
                    
                    available_models = [m for m in st.session_state.models.get(category, []) if st.session_state.active_models.get(m, True)]
                    
                    with col2:
                        model = st.selectbox("Model", available_models, key=f"model_{area}")
                    
                    production_qty = st.number_input("Production Entry Field", min_value=1, value=1, key=f"qty_{area}")
                    
                    # 2. ADD BUTTON for single entry
                    if st.form_submit_button("Add to List"):
                        if supervisor_name and model:
                            entry = {
                                "Supervisor": supervisor_name,
                                "Category": category,
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
                                        "Product": "CF"
                                    })
                                
                                st.session_state[f'temp_entries_{area}'] = [] # Clear the temporary list
                                st.success(f"✅ All {area} entries submitted successfully!")
                            else:
                                st.error("No entries in the list to submit.")
                    else:
                        st.warning("Add entries using the 'Add to List' button before submitting.")

    # === WATER DISPENSER ENTRY (Simplified) ===
    elif product_type == "💧 Water Dispenser":
        st.subheader("Water Dispenser Assembly Line Entry")
        st.info("This is a simplified entry, but the logic should mirror the Chest Freezer form for consistency.")
        # NOTE: For brevity, this uses the old simple form. It should be updated to the list/submit structure later.


# --- MODULE 3: REPORTING ---
elif menu == "3. Plan Vs Actual Report":
    st.header("📊 Production Reports")
    
    tab_wip, tab_daily, tab_monthly = st.tabs(["WIP Status", "Daily Achievement", "Monthly Report"])

    # --- WIP STATUS ---
    with tab_wip:
        st.subheader("Work In Progress (WIP) Status")
        st.warning("WIP tracking requires tracking material movement between specific areas. Displaying WIP requires more complex logic.")
        # Placeholder for future WIP visualization

    # --- DAILY ACHIEVEMENT ---
    with tab_daily:
        st.subheader("Daily Achievement Report")
        
        # 1. Date and Filter Selection
        report_date = st.date_input("Select Date", datetime.now().date(), key="daily_date")
        
        # Filter data for selected date
        date_str = report_date.strftime("%Y-%m-%d")
        daily_df = pd.DataFrame(st.session_state.production_data)
        daily_df['Report_Date'] = pd.to_datetime(daily_df['Date']).dt.strftime("%Y-%m-%d")
        filtered_df = daily_df[daily_df['Report_Date'] == date_str]
        
        # 2. Grouping and Display
        if not filtered_df.empty:
            model_summary = filtered_df.groupby(['Model', 'Category'])['Actual'].sum().reset_index()
            model_summary.rename(columns={'Actual': 'Total Actual Qty'}, inplace=True)
            st.dataframe(model_summary, hide_index=True)

            # 3. Graph
            st.markdown("#### Daily Production by Model")
            st.bar_chart(model_summary.set_index('Model')['Total Actual Qty'])
        else:
            st.info("No production data found for this date.")

    # --- MONTHLY REPORT ---
    with tab_monthly:
        st.subheader("Monthly Report (Plan vs Actual)")
        
        # Monthly filtering logic
        month_filter = st.date_input("Select Month", datetime.now().date(), format="MM/YYYY", key="monthly_date")
        month_str = month_filter.strftime("%Y-%m")
        
        monthly_df = pd.DataFrame(st.session_state.production_data)
        monthly_df['Report_Month'] = pd.to_datetime(monthly_df['Date']).dt.strftime("%Y-%m")
        monthly_filtered = monthly_df[monthly_df['Report_Month'] == month_str]
        
        if not monthly_filtered.empty:
            # Plan vs Actual Logic (using only final assembly line data for CF)
            report_data = []
            
            for model, plan_qty in st.session_state.monthly_plan.items():
                
                # Determine which subset of data to use (WD or CF Final Line)
                if 'WD' in model:
                    actual = monthly_filtered[monthly_filtered['Model'] == model]['Actual'].sum()
                elif 'CF' in model:
                    cf_final_actuals = monthly_filtered[(monthly_filtered['Model'] == model) & (monthly_filtered['Area'] == 'CF Final Line')]['Actual'].sum()
                    actual = cf_final_actuals
                else:
                    actual = monthly_filtered[monthly_filtered['Model'] == model]['Actual'].sum()

                report_data.append({
                    "Model": model,
                    "Planned Qty": plan_qty,
                    "Actual Qty": actual,
                    "Variance": actual - plan_qty
                })

            report_df = pd.DataFrame(report_data)
            
            st.dataframe(report_df.style.applymap(lambda x: 'color: red' if x < 0 else 'color: green', subset=['Variance']))
            st.bar_chart(report_df.set_index('Model')[['Planned Qty', 'Actual Qty']])
        else:
            st.info("No production data found for this month.")
