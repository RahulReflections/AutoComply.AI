import streamlit as st
import json
from openai import OpenAI

# Set your OpenAI API key here (replace with your actual API key)
OPENAI_API_KEY = "sk-proj--**"

# Instantiate OpenAI client with API key
client = OpenAI(api_key=OPENAI_API_KEY)

def call_openai_api(prompt: str, max_tokens=500):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling OpenAI API: {e}"

def load_drift_data():
    import os
    app_path = os.path.dirname(__file__)
    drift_file = os.path.abspath(os.path.join(app_path, "../data/drift_summary.json"))
    with open(drift_file, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    st.title("Compliance Drift Detector Dashboard with OpenAI Integration")

    drift_data = load_drift_data()
    st.sidebar.header(f"{len(drift_data)} Compliance Drift Issues Detected")

    selected_id = st.sidebar.selectbox("Select drift item to explore", [d["id"] for d in drift_data])
    selected = next((d for d in drift_data if d["id"] == selected_id), None)

    if not selected:
        st.error("Selected drift item not found.")
        return

    st.header(selected["description"])
    st.markdown(f"**Actual:** {selected['actual']}")
    st.markdown(f"**Expected:** {selected['expected']}")
    st.markdown(f"**Severity:** {selected['severity']}")
    st.markdown(f"**Remediation:** {selected['remediation']}")

    if st.button("Explain Drift"):
        prompt = (
            f"Explain in concise terms why this compliance drift matters:\n\n"
            f"Description: {selected['description']}\n"
            f"Actual value: {selected['actual']}\n"
            f"Expected value: {selected['expected']}\n"
            f"Severity: {selected['severity']}\n"
            "Provide relevant supporting context."
        )
        explanation = call_openai_api(prompt)
        st.markdown("### Why this matters")
        st.write(explanation)

    if st.button("Generate Remediation"):
        prompt = (
            f"Generate an idempotent, safe remediation script for the following compliance drift:\n\n"
            f"Description: {selected['description']}\n"
            f"Actual value: {selected['actual']}\n"
            f"Expected value: {selected['expected']}\n"
            "Include pre-checks, backup, verification, and rollback notes.\n"
            "Output the script code only."
        )
        remediation_script = call_openai_api(prompt)
        st.markdown("### Remediation Script")
        st.code(remediation_script, language="bash")

    if st.button("Summarize for Leadership"):
        prompt = (
            f"Write a short executive summary for leadership on this compliance drift:\n\n"
            f"Description: {selected['description']}\n"
            f"Impact: {selected['severity']}\n"
            "Include status and recommended next steps."
        )
        summary = call_openai_api(prompt)
        st.markdown("### Executive Summary")
        st.write(summary)

    st.sidebar.header("Chat/Q&A about Compliance Data")
    chat_question = st.sidebar.text_input("Ask a question about current drift results:")

    if st.sidebar.button("Submit Question") and chat_question:
        context = "\n".join(
            [f"- {d['id']}: {d['description']} (Severity: {d['severity']})" for d in drift_data]
        )
        prompt = (
            f"You are a compliance analyst. Based on the following drift items:\n{context}\n\n"
            f"Answer the question clearly and concisely:\n{chat_question}"
        )
        answer = call_openai_api(prompt)
        st.sidebar.markdown("**Answer:**")
        st.sidebar.write(answer)

if __name__ == "__main__":
    main()
