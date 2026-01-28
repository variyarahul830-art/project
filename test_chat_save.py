"""
Test script to verify chat message saving functionality
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.hasura_client import add_chat_message, get_chat_messages
import uuid

async def test_save_message():
    """Test saving a chat message"""
    print("🧪 Testing chat message save...")
    
    session_id = "test-session-" + uuid.uuid4().hex[:8]
    user_id = "test-user-123"
    message_id = "msg_" + uuid.uuid4().hex[:16]
    question = "Test question"
    answer = "Test answer"
    source = "test"
    
    print(f"📝 Creating message:")
    print(f"   Session ID: {session_id}")
    print(f"   User ID: {user_id}")
    print(f"   Message ID: {message_id}")
    print(f"   Question: {question}")
    print(f"   Answer: {answer}")
    
    try:
        result = await add_chat_message(
            message_id=message_id,
            session_id=session_id,
            user_id=user_id,
            question=question,
            answer=answer,
            source=source
        )
        print(f"✅ Message saved successfully:")
        print(f"   Result: {result}")
        
        # Try to retrieve it
        print(f"\n📥 Retrieving messages for session {session_id}...")
        messages = await get_chat_messages(session_id)
        print(f"✅ Retrieved {len(messages)} messages")
        for msg in messages:
            print(f"   - {msg}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_save_message())
