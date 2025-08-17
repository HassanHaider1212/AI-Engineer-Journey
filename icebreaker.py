from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

information = """
    How many wars occur between india & pakistan. Who won latest war?
"""

if __name__ == "__main__":
    print("Hello LLM!")

    summary_template = """
        given the information {information} about a person from I want you to create:
        1. a short summary
        2. two interesting facts about them
    """

    prompt = PromptTemplate(input_variables= ["information"], template = summary_template)

    # llm = ChatOpenAI(temperature = 0 , model = "gpt-3.5-turbo") #temperature decide upto which aspect model will be creative. 0 means no creativness.
    # llm = ChatOllama(model = "llama3")
    llm = ChatOllama(model="mistral")
    chain = prompt | llm | StrOutputParser()
    res = chain.invoke(input={"information": information})

    print(res)
