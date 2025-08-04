import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

def get_guide_response(api_key: str, city: str) -> str:
    os.environ["GOOGLE_API_KEY"] = api_key
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.8)
    
    prompt_template = PromptTemplate.from_template(
        """
        **Persona:** You are 'Amelie', a witty, modern, and super-friendly travel blogger.

        **Task:** Generate a 'Top 6 Attractions' list for {city}.
        For each attraction, provide: an emoji, **Name**, **Location**, **Why it's a must-visit**, and a **Pro Tip**.
        
        **Crucially**, after the list, conclude with a friendly question and mention that the user can ask you to **save a place** to their favorites list.
        Example closer: "So, what's on your mind? Ask me for more details on any of these, or just say **'save The Louvre'** to add it to your list! We can also switch languages if you prefer."
        """
    )
    chain = prompt_template | llm | StrOutputParser()
    return chain.invoke({"city": city})

def get_chat_response(api_key: str, messages: list) -> str:
    os.environ["GOOGLE_API_KEY"] = api_key
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.7)
    chat_history = [AIMessage(content="You are Amelie, a helpful and friendly travel guide. Continue the conversation naturally based on the user's questions.")]
    for msg in messages:
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            chat_history.append(AIMessage(content=msg["content"]))
            
    response = llm.invoke(chat_history)
    return response.content