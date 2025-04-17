import streamlit as st
import pandas as pd
import time
import os
import matplotlib.pyplot as plt
import numpy as np

# Create a folder called data in the main project folder
DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Define CSV file paths for each part of the usability testing
CONSENT_CSV = os.path.join(DATA_FOLDER, "consent_data.csv")
DEMOGRAPHIC_CSV = os.path.join(DATA_FOLDER, "demographic_data.csv")
TASK_CSV = os.path.join(DATA_FOLDER, "task_data.csv")
EXIT_CSV = os.path.join(DATA_FOLDER, "exit_data.csv")


def save_to_csv(data_dict, csv_file):
    df_new = pd.DataFrame([data_dict])
    if not os.path.isfile(csv_file):
        df_new.to_csv(csv_file, mode='w', header=True, index=False)
    else:
        df_new.to_csv(csv_file, mode='a', header=False, index=False)


def load_from_csv(csv_file):
    if os.path.isfile(csv_file):
        return pd.read_csv(csv_file)
    else:
        return pd.DataFrame()


def main():
    st.set_page_config(page_title="Usability Testing Tool")
    st.title("Usability Testing Tool")

    home, consent, demographics, tasks, exit, report = st.tabs(
        ["Home", "Consent", "Demographics", "Task", "Exit Questionnaire", "Report"])

    with home:
        st.header("Introduction")
        st.write("""
        Welcome to the Usability Testing Tool for HCI.

        In this app, you will:
        1. Provide consent for data collection.
        2. Fill out a short demographic questionnaire.
        3. Perform specific tasks using the Spotify app.
        4. Answer an exit questionnaire about your experience.
        5. View a summary report (for demonstration purposes).
        """)

    with consent:
        st.header("Consent Form")
        st.text("Please read the consent form below and confirm your agreement:")

        st.write("""
            **Consent Agreement:**
            - I understand the purpose of this usability study.
            - I am aware that my data will be collected solely for research and improvement purposes.
            - I can withdraw at any time.
        """)

        consent_given = st.checkbox("I agree to the terms above.")

        if st.button("Submit Consent"):
            if not consent_given:
                st.warning("You must agree to the consent terms before proceeding.")
            else:
                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "consent_given": consent_given
                }
                save_to_csv(data_dict, CONSENT_CSV)
                st.success("Your consent has been recorded. Thank you!")

    with demographics:
        st.header("Demographic Questionnaire")

        with st.form("demographic_form"):
            name = st.text_input("Name (optional)")
            country = st.text_input("Country of Residence (optional)")
            age = st.number_input("Age", step=1, min_value=0)
            occupation = st.text_input("Occupation")
            familiarity = st.selectbox("Familiarity with similar tools?", ["Not Familiar", "Somewhat Familiar", "Very Familiar"])

            submitted = st.form_submit_button("Submit Demographics")
            if submitted:
                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "name": name,
                    "country": country,
                    "age": age,
                    "occupation": occupation,
                    "familiarity": familiarity
                }
                save_to_csv(data_dict, DEMOGRAPHIC_CSV)
                st.success("Demographic data saved.")

    with tasks:
        st.header("Task Page")

        name2 = st.text_input("Enter your name before beginning the task:")

        task_descriptions = {
            "Authorize App": "Log into Spotify and authorize the app to access your account.",
            "View & Filter Results": "Navigate through your top songs or artists and apply filters to specify results.",
            "Export Data": "Export your listening data by downloading a CSV file."
        }

        selected_task = st.selectbox("Select Task", list(task_descriptions.keys()))
        st.write(f"**Task Description:** {task_descriptions[selected_task]}")

        if st.button("Start Task Timer"):
            st.session_state["start_time"] = time.time()
            st.info("Task timer started. Complete your task and then click 'Stop Task Timer'.")

        if st.button("Stop Task Timer") and "start_time" in st.session_state:
            duration = time.time() - st.session_state["start_time"]
            st.session_state["task_duration"] = duration
            st.success("Task completed in {:.2f} seconds!".format(duration))
            del st.session_state["start_time"]

        success = st.radio("Was the task completed successfully?", ["Yes", "No", "Partial"])
        confidence = st.slider("How confident were you while doing this task? (1 = Not Confident, 5 = Very Confident)", 1, 5, 3)
        notes = st.text_area("Observer Notes")

        if st.button("Save Task Results"):
            duration_val = st.session_state.get("task_duration", None)

            data_dict = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "user": name2,
                "task_name": selected_task,
                "success": success,
                "duration_seconds": duration_val if duration_val else "",
                "confidence_rating": confidence,
                "notes": notes
            }
            save_to_csv(data_dict, TASK_CSV)
            st.success("Task data saved.")

            for key in ["start_time", "task_duration"]:
                if key in st.session_state:
                    del st.session_state[key]

    with exit:
        st.header("Exit Questionnaire")

        with st.form("exit_form"):
            satisfaction = st.slider("Overall Satisfaction (1 = Very Low, 5 = Very High)", 1.0, 5.0)
            difficulty = st.slider("Overall Difficulty (1 = Very Easy, 5 = Very Hard)", 1.0, 5.0)
            open_feedback = st.text_area("Additional feedback or comments:")

            submitted_exit = st.form_submit_button("Submit Exit Questionnaire")
            if submitted_exit:
                data_dict = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "satisfaction": satisfaction,
                    "difficulty": difficulty,
                    "open_feedback": open_feedback
                }
                save_to_csv(data_dict, EXIT_CSV)
                st.success("Exit questionnaire data saved.")

    with report:
        st.header("Usability Report - Aggregated Results")

        with st.expander("**Consent Data**"):
            consent_df = load_from_csv(CONSENT_CSV)
            if not consent_df.empty:
                st.dataframe(consent_df)
            else:
                st.info("No consent data available yet.")

        with st.expander("**Demographic Data**"):
            demographic_df = load_from_csv(DEMOGRAPHIC_CSV)
            if not demographic_df.empty:
                st.dataframe(demographic_df)
            else:
                st.info("No demographic data available yet.")

        with st.expander("**Task Performance Data**"):
            task_df = load_from_csv(TASK_CSV)
            if not task_df.empty:
                st.dataframe(task_df)

                avg_duration = task_df.groupby('success')['duration_seconds'].mean()
                avg_duration_by_task = task_df.groupby('task_name')['duration_seconds'].mean()
                avg_duration = avg_duration.reindex(['Yes', 'Partial', 'No'])

                fig, ax = plt.subplots()
                ax.boxplot(task_df['duration_seconds'].dropna(), vert=False)
                ax.set_title('Task Completion Times')
                ax.set_xlabel('Time (seconds)')
                st.pyplot(fig)

                fig2, ax2 = plt.subplots()
                avg_duration_by_task.plot(kind='bar', ax=ax2, color='skyblue')
                ax2.set_title('Average Task Completion Time by Task')
                ax2.set_xlabel('Task Name')
                ax2.set_ylabel('Average Time (seconds)')
                st.pyplot(fig2)

                for task, duration in avg_duration_by_task.items():
                    st.write(f"**Average Time for {task}**: {duration:.2f} seconds")

                fig3, ax3 = plt.subplots()
                avg_duration.plot(kind='bar', ax=ax3, color=['green', 'orange', 'red'])
                ax3.set_title('Average Task Completion Time by Status')
                ax3.set_xlabel('Completion Status')
                ax3.set_ylabel('Average Time (seconds)')
                st.pyplot(fig3)

                for status, duration in avg_duration.items():
                    st.write(f"**Average Time for {status}**: {duration:.2f} seconds")
            else:
                st.info("No task data available yet.")

        with st.expander("**Exit Questionnaire Data**"):
            exit_df = load_from_csv(EXIT_CSV)
            if not exit_df.empty:
                st.dataframe(exit_df)

                avg_satisfaction = exit_df["satisfaction"].mean()
                avg_difficulty = exit_df["difficulty"].mean()

                fig, ax = plt.subplots()
                ax.scatter(exit_df["difficulty"], exit_df["satisfaction"])

                m, b = np.polyfit(exit_df["difficulty"], exit_df["satisfaction"], 1)
                ax.plot(exit_df["difficulty"], m*exit_df["difficulty"]+b,
                        color='green', linestyle='--', label='Best Fit')
                ax.scatter(avg_difficulty, avg_satisfaction, color='red', label='Average Point')

                ax.set_title('Satisfaction vs Difficulty')
                ax.set_xlabel('Difficulty')
                ax.set_ylabel('Satisfaction')
                ax.legend()

                st.pyplot(fig)

                st.write(f"**Average Satisfaction**: {avg_satisfaction:.2f}")
                st.write(f"**Average Difficulty**: {avg_difficulty:.2f}")
            else:
                st.info("No exit questionnaire data available yet.")


if __name__ == "__main__":
    main()
