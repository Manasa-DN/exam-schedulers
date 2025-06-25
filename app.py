import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import io

st.title("📅 Exam Timetable Scheduler using Graph Coloring")

# Step 1: Upload CSV
uploaded_file = st.file_uploader("Upload student_exam_data.csv", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    if "student_id" not in df.columns or "exam" not in df.columns:
        st.error("CSV must have 'student_id' and 'exam' columns.")
        st.stop()

    # Step 2: Build conflict graph
    exam_students = defaultdict(set)
    student_exams = defaultdict(set)
    for _, row in df.iterrows():
        student_id, exam = row["student_id"], row["exam"]
        exam_students[exam].add(student_id)
        student_exams[student_id].add(exam)

    exams = list(exam_students.keys())
    graph = nx.Graph()
    graph.add_nodes_from(exams)

    for i in range(len(exams)):
        for j in range(i + 1, len(exams)):
            exam1, exam2 = exams[i], exams[j]
            if exam_students[exam1] & exam_students[exam2]:
                graph.add_edge(exam1, exam2)

    # Step 3: Graph coloring
    time_slots = nx.coloring.greedy_color(graph, strategy='largest_first')
    slot_to_exams = defaultdict(list)
    for exam, slot in time_slots.items():
        slot_to_exams[slot].append(exam)

    # Step 4: Display timetable
    st.subheader("🗓️ Timetable (Time Slot → Exams)")
    timetable_data = []
    for slot in sorted(slot_to_exams):
        exams_in_slot = sorted(slot_to_exams[slot])
        st.markdown(f"**Time Slot {slot + 1}**: {', '.join(exams_in_slot)}")
        for exam in exams_in_slot:
            timetable_data.append({"Time Slot": slot + 1, "Exam": exam})

    df_timetable = pd.DataFrame(timetable_data)

    # Step 5: Download CSV
    csv_buffer = io.StringIO()
    df_timetable.to_csv(csv_buffer, index=False)
    st.download_button("⬇️ Download Timetable CSV", data=csv_buffer.getvalue(), file_name="exam_timetable.csv", mime="text/csv")

    # Step 6: Visualize conflict graph
    st.subheader("📊 Conflict Graph (Partial View)")
    subgraph_nodes = list(graph.nodes())[:20]
    subgraph = graph.subgraph(subgraph_nodes)
    colors = [time_slots[exam] for exam in subgraph.nodes()]
    labels = {exam: f"{exam}\n(Slot {time_slots[exam]+1})" for exam in subgraph.nodes()]

    fig, ax = plt.subplots(figsize=(12, 8))
    nx.draw(
        subgraph,
        labels=labels,
        with_labels=True,
        node_color=colors,
        cmap=plt.cm.Set3,
        node_size=2500,
        font_size=8,
        edge_color='gray',
        ax=ax
    )
    st.pyplot(fig)
