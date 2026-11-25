import streamlit as st

from course_solver import read_choices, solve


st.set_page_config(page_title="Course Grouping", layout="wide")
st.title("Course Grouping")
st.write("Find course groups that minimize the highest number of shared students between any two courses in a group.")

with st.form("grouping"):
    upload = st.file_uploader("Student course choices CSV", type=["csv"])
    st.caption("The CSV needs student_id and course_id columns.")
    cutoff = st.number_input(
        "Overlap cutoff",
        min_value=1,
        value=20,
        step=1,
        help="Each pair must share fewer students than the cutoff. Enter 21 to allow exactly 20.",
    )
    group_sizes = st.text_input(
        "Group sizes",
        value="2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1",
        help="Enter comma-separated positive whole numbers that add up to the number of distinct courses.",
    )
    submitted = st.form_submit_button("Find groups", type="primary")

if submitted:
    if upload is None:
        st.error("Choose a student course choices CSV.")
        st.stop()

    try:
        sizes = [int(value) for value in group_sizes.split(",")]
        if any(size < 1 for size in sizes):
            raise ValueError
    except ValueError:
        st.error("Enter positive whole numbers separated by commas for the group sizes.")
        st.stop()

    try:
        courses, overlaps = read_choices(upload.getvalue().decode("utf-8-sig"))
        with st.spinner("Finding groups with the lowest possible pairwise overlap…"):
            groups = solve(overlaps, sizes, cutoff)
    except UnicodeDecodeError:
        st.error("Save the CSV with UTF-8 encoding and upload it again.")
        st.stop()
    except ValueError as error:
        st.error(str(error))
        st.stop()

    if groups is None:
        st.warning(f"No grouping fits these sizes with every pair sharing fewer than {cutoff} students.")
        st.stop()

    st.subheader("Results")
    st.write(f"{len(courses)} courses in {len(groups)} groups.")
    summary = []
    pairs = []
    for group_number, group in enumerate(groups, start=1):
        summary.append({"Group": group_number, "Courses": ", ".join(courses[i] for i in group)})
        for position, first in enumerate(group):
            for second in group[position + 1:]:
                pairs.append({
                    "Group": group_number,
                    "Course 1": courses[first],
                    "Course 2": courses[second],
                    "Shared students": overlaps[first][second],
                })

    if pairs:
        st.metric("Highest pairwise overlap", max(pair["Shared students"] for pair in pairs))
    st.dataframe(summary, hide_index=True)
    if pairs:
        st.subheader("Pairwise overlaps")
        st.dataframe(pairs, hide_index=True)
