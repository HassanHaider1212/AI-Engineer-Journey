"""
AI Chatbot Backend - FastAPI Application

A production-ready chatbot backend with LangChain integration,
memory management, and real-time communication.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio
import logging
from datetime import datetime
import uuid

from src.agents.chatbot_agent import ChatbotAgent
from src.models.conversation import Conversation, Message
from src.services.memory_service import MemoryService
from src.utils.config import Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize settings
settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title="AI Chatbot API",
    description="A production-ready AI chatbot with LangChain integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
memory_service = MemoryService()
chatbot_agent = ChatbotAgent(settings)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_sessions: Dict[str, str] = {}  # websocket_id -> user_id

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_sessions[id(websocket)] = user_id
        logger.info(f"User {user_id} connected")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            user_id = self.user_sessions.pop(id(websocket), None)
            logger.info(f"User {user_id} disconnected")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")

manager = ConnectionManager()

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    user_id: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    message_id: str

class ConversationHistory(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]

# API Endpoints
@app.get("/")
async def root():
    return {"message": "AI Chatbot API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """
    Send a message to the chatbot and get a response.
    """
    try:
        # Generate session ID if not provided
        session_id = chat_message.session_id or str(uuid.uuid4())
        
        # Get conversation history
        conversation = await memory_service.get_conversation(session_id)
        
        # Add user message
        user_message = Message(
            role="user",
            content=chat_message.message,
            timestamp=datetime.now()
        )
        conversation.add_message(user_message)
        
        # Get AI response
        ai_response = await chatbot_agent.generate_response(
            message=chat_message.message,
            conversation_history=conversation.get_messages()
        )
        
        # Add AI response
        ai_message = Message(
            role="assistant",
            content=ai_response,
            timestamp=datetime.now()
        )
        conversation.add_message(ai_message)
        
        # Save conversation
        await memory_service.save_conversation(session_id, conversation)
        
        return ChatResponse(
            response=ai_response,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            message_id=str(uuid.uuid4())
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation/{session_id}", response_model=ConversationHistory)
async def get_conversation(session_id: str):
    """
    Get conversation history for a session.
    """
    try:
        conversation = await memory_service.get_conversation(session_id)
        return ConversationHistory(
            session_id=session_id,
            messages=[msg.to_dict() for msg in conversation.get_messages()]
        )
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=404, detail="Conversation not found")

@app.delete("/conversation/{session_id}")
async def delete_conversation(session_id: str):
    """
    Delete a conversation session.
    """
    try:
        await memory_service.delete_conversation(session_id)
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations")
async def list_conversations():
    """
    List all conversation sessions.
    """
    try:
        conversations = await memory_service.list_conversations()
        return {"conversations": conversations}
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time chat
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message
            session_id = message_data.get("session_id", str(uuid.uuid4()))
            message = message_data.get("message", "")
            
            # Get conversation history
            conversation = await memory_service.get_conversation(session_id)
            
            # Add user message
            user_message = Message(
                role="user",
                content=message,
                timestamp=datetime.now()
            )
            conversation.add_message(user_message)
            
            # Get AI response
            ai_response = await chatbot_agent.generate_response(
                message=message,
                conversation_history=conversation.get_messages()
            )
            
            # Add AI response
            ai_message = Message(
                role="assistant",
                content=ai_response,
                timestamp=datetime.now()
            )
            conversation.add_message(ai_message)
            
            # Save conversation
            await memory_service.save_conversation(session_id, conversation)
            
            # Send response back to client
            response_data = {
                "response": ai_response,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "message_id": str(uuid.uuid4())
            }
            
            await manager.send_personal_message(
                json.dumps(response_data), 
                websocket
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Serve HTML page for testing
@app.get("/test", response_class=HTMLResponse)
async def test_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Chatbot Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #chat { border: 1px solid #ccc; height: 400px; overflow-y: scroll; padding: 10px; }
            #input { width: 80%; padding: 10px; }
            #send { padding: 10px; }
        </style>
    </head>
    <body>
        <h1>AI Chatbot Test</h1>
        <div id="chat"></div>
        <input type="text" id="input" placeholder="Type your message...">
        <button id="send">Send</button>
        
        <script>
            const ws = new WebSocket("ws://localhost:8000/ws/test-user");
            const chat = document.getElementById("chat");
            const input = document.getElementById("input");
            const send = document.getElementById("send");
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                const messageDiv = document.createElement("div");
                messageDiv.innerHTML = `<strong>AI:</strong> ${data.response}`;
                chat.appendChild(messageDiv);
                chat.scrollTop = chat.scrollHeight;
            };
            
            send.onclick = function() {
                const message = input.value;
                if (message) {
                    const messageDiv = document.createElement("div");
                    messageDiv.innerHTML = `<strong>You:</strong> ${message}`;
                    chat.appendChild(messageDiv);
                    
                    ws.send(JSON.stringify({
                        message: message,
                        session_id: "test-session"
                    }));
                    
                    input.value = "";
                    chat.scrollTop = chat.scrollHeight;
                }
            };
            
            input.onkeypress = function(e) {
                if (e.key === "Enter") {
                    send.click();
                }
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
