
import streamlit as st
import pandas as pd
from pathlib import Path
import pymupdf

jobs_path = Path(__file__).resolve().parent / "jobs.csv"
jobs = pd.read_csv(jobs_path)


def calculate_match(candidate_skills, required_skills):

    candidate = {
        skill.strip().lower()
        for skill in candidate_skills.split(",")
        if skill.strip()
    }

    required = {
        skill.strip().lower()
        for skill in required_skills.split(";")
        if skill.strip()
    }

    matched = candidate.intersection(required)
    missing = required.difference(candidate)

    score = round(len(matched) / len(required) * 100) if required else 0

    return score, sorted(matched), sorted(missing)



def extract_cv_text(uploaded_file):
    pdf_bytes = uploaded_file.getvalue()

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
        text = ""

        for page in document:
            text += page.get_text() + "\n"

    return text




def detect_skills(cv_text, jobs):
    import re

    known_skills = set()

    for skill_list in jobs["skills"]:
        for skill in skill_list.split(";"):
            known_skills.add(skill.strip().lower())

    cv_text = cv_text.lower()
    detected = []

    for skill in known_skills:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, cv_text):
            detected.append(skill)

    return sorted(detected)


st.set_page_config(
    page_title="TalentMatch AI",
    page_icon=":material/neurology:",
    layout="wide"
)

st.title(":material/neurology: TalentMatch AI")
st.write("Discover job opportunities that match your skills.")

st.divider()

st.subheader(":material/person: Candidate Profile")

name = st.text_input("Your name")

uploaded_cv = st.file_uploader(
    "Upload your CV",
    type=["pdf"],
    help="Upload your CV in PDF format",
)


cv_text = ""
detected_skills = []

if uploaded_cv is not None:
    try:
        cv_text = extract_cv_text(uploaded_cv)

        st.success("CV uploaded and read successfully!")

        detected_skills = detect_skills(cv_text, jobs)

        if detected_skills:
            st.write("**Skills detected from your CV:**")
            st.write(", ".join(detected_skills))
        else:
            st.warning("No matching skills were detected in this CV.")

    except Exception:
        st.error("We couldn't read this PDF. Please try another file.")

skills = st.text_area(
    "Your skills and experience",
    value=", ".join(detected_skills),
    placeholder="Example: Excel, Python, SQL, teamwork..."
)



if st.button("Find my matches"):
    if skills.strip():
        st.success("Profile received!")
        st.write("Candidate:", name)
        st.write("Skills:", skills)

        
        st.subheader(":material/target: Your recommended jobs")

        recommendations = []

        for _, job in jobs.iterrows():

            score, matched, missing = calculate_match(
                skills,
                job["skills"]
            )

            recommendations.append({
                "title": job["title"],
                "company": job["company"],
                "score": score,
                "matched": matched,
                "missing": missing
            })

        recommendations.sort(
            key=lambda job: job["score"],
            reverse=True
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Jobs analyzed", len(recommendations))
        col2.metric("Best match", f"{recommendations[0]['score']}%")
        col3.metric(
            "Matching opportunities",
            sum(job["score"] > 0 for job in recommendations)
        )

        st.divider()

        for job in recommendations:

            with st.container(border=True):

                st.subheader(job["title"])
                st.caption(job["company"])

                st.progress(job["score"] / 100)

                st.write(f"**Skill match: {job['score']}%**")

                if job["matched"]:
                    st.success(
                        "✓ Matching skills: "
                        + ", ".join(job["matched"])
                    )

                if job["missing"]:
                    st.info(
                        "Skills to develop: "
                        + ", ".join(job["missing"])
                    )

 
    else:
        st.warning("Please enter your skills.")

