import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="Bi-Weekly Wage Calculator", layout="wide")
st.title("Bi-Weekly Wage Calculator")

BONUS_FOR_12H = 35

# Sidebar Rate Inputs
st.sidebar.header("Rates Settings")
regular_rate = st.sidebar.number_input("Regular Hourly Wage ($)", min_value=0.0, value=24.0, step=0.5)
overtime_multiplier = st.sidebar.number_input("Overtime Multiplier", min_value=1.0, value=1.5, step=0.1)
km_rate = st.sidebar.number_input("Kilometer Rate ($/km)", min_value=0.0, value=0.50, step=0.01)
overtime_rate = regular_rate * overtime_multiplier

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def calculate_day_pay(start_time, end_time, km_driven, misc_pay, regular_rate, overtime_rate, km_rate, day_name):
    start_dt = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
    total_hours = (end_dt - start_dt).total_seconds() / 3600

    if day_name in ["Saturday", "Sunday"]:
        reg_hours = 0
        ot_hours = total_hours
    else:
        regular_start = datetime.combine(datetime.today(), datetime.strptime("08:00", "%H:%M").time())
        regular_end = datetime.combine(datetime.today(), datetime.strptime("17:00", "%H:%M").time())

        regular_work_start = max(start_dt, regular_start)
        regular_work_end = min(end_dt, regular_end)
        reg_hours = max(0, (regular_work_end - regular_work_start).total_seconds() / 3600)
        ot_hours = total_hours - reg_hours

    bonus = BONUS_FOR_12H if total_hours >= 12 else 0
    km_pay = km_driven * km_rate
    regular_pay = reg_hours * regular_rate
    overtime_pay = ot_hours * overtime_rate
    total_pay = regular_pay + overtime_pay + bonus + km_pay + misc_pay

    return {
        "Regular Hours": reg_hours,
        "Overtime Hours": ot_hours,
        "Total Hours": total_hours,
        "Regular Pay": regular_pay,
        "Overtime Pay": overtime_pay,
        "Bonus": bonus,
        "KM Pay": km_pay,
        "Misc Pay": misc_pay,
        "Total Pay": total_pay
    }

def input_week_data(week_number):
    st.header(f"Week {week_number} Work Details")
    week_data = []

    for day in days:
        st.subheader(day)
        worked = st.checkbox(f"Did you work on {day} (Week {week_number})?", value=False, key=f"w{week_number}_{day}_worked")
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)

        if worked:
            with col1:
                left_home = st.time_input(f"{day} Time Left Home", value=datetime.strptime("07:30", "%H:%M").time(), key=f"w{week_number}_{day}_left")
            with col2:
                arrived_company = st.time_input(f"{day} Arrived at Company", value=datetime.strptime("08:00", "%H:%M").time(), key=f"w{week_number}_{day}_arrived")
            with col3:
                finished_company = st.time_input(f"{day} Finished at Company", value=datetime.strptime("17:00", "%H:%M").time(), key=f"w{week_number}_{day}_finished")
            with col4:
                reached_home = st.time_input(f"{day} Time Reached Home", value=datetime.strptime("17:30", "%H:%M").time(), key=f"w{week_number}_{day}_reached")

            km_driven = st.number_input(f"{day} Kilometers Driven (Week {week_number})", min_value=0.0, value=0.0, key=f"w{week_number}_{day}_km")
            misc_pay = st.number_input(f"{day} Miscellaneous Pay ($)", min_value=0.0, value=0.0, key=f"w{week_number}_{day}_misc")
            notes = st.text_area(f"{day} Notes (optional)", value="", key=f"w{week_number}_{day}_notes")
        else:
            st.info(f"No work recorded for {day}. All inputs disabled.")
            left_home = arrived_company = finished_company = reached_home = datetime.strptime("00:00", "%H:%M").time()
            km_driven = misc_pay = 0.0
            notes = ""

            with col1:
                st.time_input(f"{day} Time Left Home", value=left_home, key=f"w{week_number}_{day}_left", disabled=True)
            with col2:
                st.time_input(f"{day} Arrived at Company", value=arrived_company, key=f"w{week_number}_{day}_arrived", disabled=True)
            with col3:
                st.time_input(f"{day} Finished at Company", value=finished_company, key=f"w{week_number}_{day}_finished", disabled=True)
            with col4:
                st.time_input(f"{day} Time Reached Home", value=reached_home, key=f"w{week_number}_{day}_reached", disabled=True)

            st.number_input(f"{day} Kilometers Driven (Week {week_number})", value=km_driven, key=f"w{week_number}_{day}_km", disabled=True)
            st.number_input(f"{day} Miscellaneous Pay ($)", value=misc_pay, key=f"w{week_number}_{day}_misc", disabled=True)

        day_pay = calculate_day_pay(left_home, reached_home, km_driven, misc_pay, regular_rate, overtime_rate, km_rate, day)
        day_pay.update({
            "Left Home": left_home,
            "Arrived Company": arrived_company,
            "Finished Company": finished_company,
            "Reached Home": reached_home,
            "Notes": notes
        })
        week_data.append((day, day_pay))

    return week_data

tab1, tab2 = st.tabs(["Week 1", "Week 2"])
with tab1: week1_data = input_week_data(1)
with tab2: week2_data = input_week_data(2)

def display_summary(week_data, week_number):
    with st.expander(f"Week {week_number} Summary", expanded=False):
        summary_rows = []
        for day, data in week_data:
            summary_rows.append({
                "Day": day,
                "Reg. Hrs": f"{data['Regular Hours']:.2f}",
                "Overtime": f"{data['Overtime Hours']:.2f}",
                "Total Hours": f"{data['Total Hours']:.2f}",
                "Total Pay ($)": f"{data['Total Pay']:.2f}"
            })
        df = pd.DataFrame(summary_rows)
        st.table(df)
        total_weekly_pay = sum(data["Total Pay"] for _, data in week_data)
        st.markdown(f"### Total Pay for Week {week_number}: ${total_weekly_pay:.2f}")
        return total_weekly_pay

total_week1 = display_summary(week1_data, 1)
total_week2 = display_summary(week2_data, 2)
total_biweekly = total_week1 + total_week2
st.markdown(f"# *Total Bi-Weekly Pay: ${total_biweekly:.2f}*")

def create_hours_report(week1_data, week2_data):
    rows = []
    for week_num, week_data in [(1, week1_data), (2, week2_data)]:
        for day, data in week_data:
            if data["Total Hours"] > 0:
                misc_value = data["Misc Pay"]
                misc_str = ""
                if misc_value > 0 and data["Total Hours"] >= 12:
                    misc_str = f"{misc_value:.2f} + 35"
                elif misc_value > 0:
                    misc_str = f"{misc_value:.2f}"
                elif data["Total Hours"] >= 12:
                    misc_str = "35"

                row = {
                    "Week": f"Week {week_num}",
                    "Day": day,
                    "Left Home": data["Left Home"].strftime("%H:%M"),
                    "Arrived at Company": data["Arrived Company"].strftime("%H:%M"),
                    "Finished at Company": data["Finished Company"].strftime("%H:%M"),
                    "Reached Home": data["Reached Home"].strftime("%H:%M"),
                    "KM Driven": f"{data['KM Pay'] / km_rate:.2f}",
                    "Reg. Hr": f"{data['Regular Hours']:.2f}",
                    "Overtime": f"{data['Overtime Hours']:.2f}",
                    "Notes": data["Notes"]
                }
                if misc_str:
                    row["Misc"] = misc_str

                rows.append(row)
    return pd.DataFrame(rows)

report_df = create_hours_report(week1_data, week2_data)
csv = report_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📄 Download Worked Days Report (CSV)",
    data=csv,
    file_name='worked_hours_report.csv',
    mime='text/csv'
)
