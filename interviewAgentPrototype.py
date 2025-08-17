import streamlit as st
from langchain_core.prompts import PromptTemplate
# from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key=st.secrets["OPENAI_API_KEY"]
)
# Load your local Ollama model (cached by Streamlit)
# @st.cache_resource
# def load_model():
#     return ChatOllama(model="mistral")   # or "llama3", depending on what you have installed
#
# llm = load_model()

# Role-based questions
ROLE_QUESTIONS = {
    "Developer": [
        "Can you explain the concept of RESTful APIs?",
        "Describe a challenging bug you fixed recently.",
        "How do you ensure code quality in a team setting?"
    ],
    "Designer": [
        "How do you approach user research?",
        "Tell me about a design project you're proud of.",
        "How do you balance creativity with usability?"
    ],
    "HR": [
        "How do you handle conflict between team members?",
        "Describe your experience with talent acquisition.",
        "What strategies do you use to improve employee retention?"
    ]
}

st.title("🧠 AI Interview Assistant")

# Select role
role = st.selectbox("Choose Interview Role", list(ROLE_QUESTIONS.keys()))

# Start interview
if st.button("Start Interview"):
    st.session_state.questions = ROLE_QUESTIONS[role]
    st.session_state.current = 0
    st.session_state.responses = []

# Interview loop
if "questions" in st.session_state and st.session_state.current < len(st.session_state.questions):
    q = st.session_state.questions[st.session_state.current]
    st.subheader(f"Question {st.session_state.current + 1}:")
    st.write(q)

    user_input = st.text_area("Your Answer", key=f"answer_{st.session_state.current}")
    if st.button("Submit Answer"):
        st.session_state.responses.append({"question": q, "answer": user_input})
        st.session_state.current += 1

# Show feedback
if "questions" in st.session_state and st.session_state.current == len(st.session_state.questions):
    st.success("Interview Complete! Generating Feedback...")

    for i, resp in enumerate(st.session_state.responses):
        prompt = PromptTemplate(
            input_variables=["question", "answer"],
            template="""
            Evaluate this interview response:
            Question: {question}
            Answer: {answer}
            Provide constructive feedback and a score out of 10.
            """
        )
        chain = prompt | llm | StrOutputParser()
        feedback = chain.invoke({"question": resp["question"], "answer": resp["answer"]})

        st.markdown(f"**Q{i+1}:** {resp['question']}")
        st.markdown(f"**Your Answer:** {resp['answer']}")
        st.markdown(f"**AI Feedback:** {feedback}")
        st.divider()
