import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

st.markdown("<h1 style='color:#4CAF50'>💰 Bi-Weekly Wage Calculator</h1>", unsafe_allow_html=True)

# Constants
REGULAR_RATE = 24
OVERTIME_RATE = 36
BONUS_FOR_12H = 35
KM_RATE = 0.50

def calculate_day_pay(start_time, end_time, km_driven, misc_pay, day_name):
    start_dt = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
    total_hours = (end_dt - start_dt).total_seconds() / 3600

    # For weekends, all hours count as overtime
    if day_name in ["Saturday", "Sunday"]:
        reg_hours = 0
        ot_hours = total_hours
    else:
        regular_start = datetime.combine(datetime.today(), datetime.strptime("08:00", "%H:%M").time())
        regular_end = datetime.combine(datetime.today(), datetime.strptime("17:00", "%H:%M").time())

        reg_hours = 0
        ot_hours = 0
        current = start_dt
        while current < end_dt:
            next_hour = current + timedelta(hours=1)
            if next_hour > end_dt:
                next_hour = end_dt
            if regular_start <= current < regular_end:
                reg_hours += (next_hour - current).total_seconds() / 3600
            else:
                ot_hours += (next_hour - current).total_seconds() / 3600
            current = next_hour

    bonus = BONUS_FOR_12H if total_hours >= 12 else 0
    km_pay = km_driven * KM_RATE

    regular_pay = reg_hours * REGULAR_RATE
    overtime_pay = ot_hours * OVERTIME_RATE
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

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def input_week_data(week_number):
    st.header(f"Week {week_number} Work Details")
    week_data = []
    for day in days:
        st.subheader(day)
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input(
                f"{day} Start Time (Week {week_number})",
                value=datetime.strptime("00:00", "%H:%M").time(),
                key=f"w{week_number}_{day}_start"
            )
        with col2:
            end_time = st.time_input(
                f"{day} End Time (Week {week_number})",
                value=datetime.strptime("00:00", "%H:%M").time(),
                key=f"w{week_number}_{day}_end"
            )
        km_driven = st.number_input(
            f"{day} Kilometers Driven (Week {week_number})",
            min_value=0.0,
            value=0.0,
            key=f"w{week_number}_{day}_km"
        )
        misc_pay = st.number_input(
            f"{day} Miscellaneous Pay ($) (Week {week_number})",
            min_value=0.0,
            value=0.0,
            key=f"w{week_number}_{day}_misc"
        )

        day_pay = calculate_day_pay(start_time, end_time, km_driven, misc_pay, day)
        week_data.append((day, day_pay))
    return week_data

def display_summary(week_data, week_number):
    summary_rows = []
    for day, data in week_data:
        summary_rows.append({
            "Day": day,
            "Regular Hours": f"{data['Regular Hours']:.2f}",
            "Overtime Hours": f"{data['Overtime Hours']:.2f}",
            "Total Hours": f"{data['Total Hours']:.2f}",
            "Total Pay ($)": f"{data['Total Pay']:.2f}"
        })
    df = pd.DataFrame(summary_rows)
    total_weekly_pay = sum(data["Total Pay"] for _, data in week_data)

    # Use an expander collapsed by default
    with st.expander(f"Week {week_number} Summary (Click to expand)", expanded=False):
        st.table(df)
        st.markdown(f"### Total Pay for Week {week_number}: ${total_weekly_pay:.2f}")

    return total_weekly_pay

tab1, tab2 = st.tabs(["Week 1", "Week 2"])

with tab1:
    with st.expander("Enter Week 1 Work Details", expanded=True):
        week1_data = input_week_data(1)
    if 'week1_data' in locals():
        total_week1 = display_summary(week1_data, 1)
    else:
        total_week1 = 0

with tab2:
    with st.expander("Enter Week 2 Work Details", expanded=True):
        week2_data = input_week_data(2)
    if 'week2_data' in locals():
        total_week2 = display_summary(week2_data, 2)
    else:
        total_week2 = 0

total_biweekly = (total_week1 if 'total_week1' in locals() else 0) + (total_week2 if 'total_week2' in locals() else 0)

# Show summary metrics outside tabs
col1, col2, col3 = st.columns(3)
col1.metric("Week 1 Total Pay", f"${total_week1:.2f}" if 'total_week1' in locals() else "$0.00")
col2.metric("Week 2 Total Pay", f"${total_week2:.2f}" if 'total_week2' in locals() else "$0.00")
col3.metric("Bi-Weekly Total Pay", f"${total_biweekly:.2f}")

def create_hours_report(week1_data, week2_data):
    rows = []
    for week_num, week_data in [(1, week1_data), (2, week2_data)]:
        for day, data in week_data:
            if data["Total Hours"] > 0:
                start_key = f"w{week_num}_{day}_start"
                end_key = f"w{week_num}_{day}_end"
                km_key = f"w{week_num}_{day}_km"

                start_time = st.session_state[start_key].strftime("%H:%M")
                end_time = st.session_state[end_key].strftime("%H:%M")
                kms = st.session_state[km_key]
                reg_hours = round(data["Regular Hours"], 2)
                ot_hours = round(data["Overtime Hours"], 2)

                rows.append({
                    "Week": f"Week {week_num}",
                    "Day": day,
                    "Start Time": start_time,
                    "End Time": end_time,
                    "KM Driven": kms,
                    "Regular Hours": reg_hours,
                    "Overtime Hours": ot_hours
                })
    df = pd.DataFrame(rows)
    return df

if ('week1_data' in locals()) and ('week2_data' in locals()):
    report_df = create_hours_report(week1_data, week2_data)
    csv = report_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📄 Download Worked Days Report (CSV)",
        data=csv,
        file_name='worked_hours_report.csv',
        mime='text/csv'
    )
