"""
Chatbot Agent - LangChain-powered conversational AI

This module implements a sophisticated chatbot agent with memory,
context awareness, and tool integration.
"""

from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain_core.runnables import RunnablePassthrough
import logging
from datetime import datetime

from src.utils.config import Settings
from src.models.conversation import Message

logger = logging.getLogger(__name__)

class ChatbotAgent:
    """
    Advanced chatbot agent with LangChain integration.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = self._initialize_llm()
        self.memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 exchanges
            return_messages=True
        )
        self.tools = self._initialize_tools()
        self.agent = self._create_agent()
        
    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the language model."""
        return ChatOpenAI(
            model=self.settings.openai_model,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
            api_key=self.settings.openai_api_key
        )
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize tools for the agent."""
        return [
            Tool(
                name="get_current_time",
                description="Get the current date and time",
                func=self._get_current_time
            ),
            Tool(
                name="calculate",
                description="Perform basic mathematical calculations",
                func=self._calculate
            ),
            Tool(
                name="search_knowledge",
                description="Search the knowledge base for information",
                func=self._search_knowledge
            )
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """Create the agent with tools and memory."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        return """
        You are a helpful, knowledgeable, and friendly AI assistant. You can help users with:
        
        1. General questions and conversations
        2. Mathematical calculations
        3. Current time and date information
        4. Knowledge base searches
        5. Problem-solving and analysis
        
        Guidelines:
        - Be helpful, accurate, and concise
        - Use tools when appropriate to provide accurate information
        - Maintain context from previous messages in the conversation
        - If you don't know something, say so and offer to help in other ways
        - Be friendly and engaging in your responses
        
        Always strive to provide the most helpful and accurate response possible.
        """
    
    async def generate_response(
        self, 
        message: str, 
        conversation_history: List[Message]
    ) -> str:
        """
        Generate a response to a user message.
        
        Args:
            message: The user's message
            conversation_history: Previous messages in the conversation
            
        Returns:
            The AI's response
        """
        try:
            # Update memory with conversation history
            self._update_memory(conversation_history)
            
            # Generate response using the agent
            response = await self.agent.ainvoke({"input": message})
            
            return response.get("output", "I'm sorry, I couldn't generate a response.")
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, I encountered an error while processing your message. Please try again."
    
    def _update_memory(self, conversation_history: List[Message]):
        """Update the agent's memory with conversation history."""
        # Clear existing memory
        self.memory.clear()
        
        # Add recent messages to memory
        for msg in conversation_history[-10:]:  # Keep last 10 messages
            if msg.role == "user":
                self.memory.chat_memory.add_user_message(msg.content)
            elif msg.role == "assistant":
                self.memory.chat_memory.add_ai_message(msg.content)
    
    # Tool implementations
    def _get_current_time(self, query: str) -> str:
        """Get the current time."""
        now = datetime.now()
        return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def _calculate(self, expression: str) -> str:
        """Perform basic mathematical calculations."""
        try:
            # Simple evaluation for basic math (be careful with this in production)
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error calculating '{expression}': {str(e)}"
    
    def _search_knowledge(self, query: str) -> str:
        """Search the knowledge base."""
        # This is a placeholder - in a real implementation, you would
        # integrate with a vector database or knowledge base
        return f"Knowledge search for '{query}': This is a placeholder response. In a real implementation, this would search your knowledge base."
    
    def reset_memory(self):
        """Reset the agent's memory."""
        self.memory.clear()
        logger.info("Agent memory reset")
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of the agent's memory."""
        return {
            "memory_type": "ConversationBufferWindowMemory",
            "buffer_size": self.memory.k,
            "current_messages": len(self.memory.chat_memory.messages)
        }
