"""
Chat Copilot Component for AI Packaging Reliability Copilot Dashboard
Natural language interaction with IBM Bob
"""

import streamlit as st
from typing import List, Dict, Optional
from datetime import datetime


def render_chat_interface(api_client, current_data: Optional[Dict] = None):
    """
    Render chat interface for copilot interaction
    
    Args:
        api_client: API client instance
        current_data: Current process data for context
    """
    st.markdown("### 💬 Chat with AI Copilot")
    st.markdown("Ask me anything about the packaging process, current status, or how to optimize parameters.")
    
    # Initialize chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        if not st.session_state.chat_history:
            st.info("👋 Hi! I'm your AI packaging reliability copilot. How can I help you today?")
            
            # Show example queries
            st.markdown("**Try asking:**")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔍 Why is this batch severe?"):
                    process_query("Why is this batch severe?", api_client, current_data)
                if st.button("📊 Analyze wire bonding"):
                    process_query("Analyze wire bonding", api_client, current_data)
            with col2:
                if st.button("💡 How can I optimize?"):
                    process_query("How can I optimize this process?", api_client, current_data)
                if st.button("❓ Explain die attach"):
                    process_query("Explain die attach stage", api_client, current_data)
        else:
            # Display chat messages
            for message in st.session_state.chat_history:
                render_chat_message(message)
    
    # Input area
    st.markdown("---")
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Your question:",
            key="chat_input",
            placeholder="Type your question here...",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send", use_container_width=True)
    
    # Process input
    if send_button and user_input:
        process_query(user_input, api_client, current_data)
        st.rerun()
    
    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()


def render_chat_message(message: Dict):
    """
    Render a single chat message
    
    Args:
        message: Message dictionary with role, content, timestamp
    """
    role = message.get('role', 'user')
    content = message.get('content', '')
    timestamp = message.get('timestamp', '')
    confidence = message.get('confidence')
    query_type = message.get('query_type')
    
    if role == 'user':
        # User message (right-aligned, blue)
        st.markdown(
            f"""
            <div style="
                display: flex;
                justify-content: flex-end;
                margin: 10px 0;
            ">
                <div style="
                    background-color: #1f77b4;
                    color: white;
                    padding: 12px 16px;
                    border-radius: 18px;
                    max-width: 70%;
                    word-wrap: break-word;
                ">
                    <div style="font-size: 14px;">{content}</div>
                    <div style="font-size: 10px; opacity: 0.8; margin-top: 5px;">
                        {timestamp}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Assistant message (left-aligned, gray)
        confidence_badge = ""
        if confidence is not None:
            confidence_pct = confidence * 100
            color = "#28a745" if confidence > 0.8 else "#ffc107" if confidence > 0.6 else "#dc3545"
            confidence_badge = f"""
                <span style="
                    background-color: {color};
                    color: white;
                    padding: 2px 8px;
                    border-radius: 10px;
                    font-size: 10px;
                    margin-left: 10px;
                ">
                    {confidence_pct:.0f}% confident
                </span>
            """
        
        type_badge = ""
        if query_type:
            type_badge = f"""
                <span style="
                    background-color: #6c757d;
                    color: white;
                    padding: 2px 8px;
                    border-radius: 10px;
                    font-size: 10px;
                    margin-left: 5px;
                ">
                    {query_type}
                </span>
            """
        
        st.markdown(
            f"""
            <div style="
                display: flex;
                justify-content: flex-start;
                margin: 10px 0;
            ">
                <div style="
                    background-color: #f1f3f4;
                    color: #202124;
                    padding: 12px 16px;
                    border-radius: 18px;
                    max-width: 70%;
                    word-wrap: break-word;
                    border-left: 4px solid #1f77b4;
                ">
                    <div style="font-weight: bold; margin-bottom: 5px; color: #1f77b4;">
                        🤖 AI Copilot {confidence_badge} {type_badge}
                    </div>
                    <div style="font-size: 14px; line-height: 1.5;">
                        {content}
                    </div>
                    <div style="font-size: 10px; color: #666; margin-top: 5px;">
                        {timestamp}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def process_query(query: str, api_client, current_data: Optional[Dict]):
    """
    Process user query and get copilot response
    
    Args:
        query: User query
        api_client: API client instance
        current_data: Current process data
    """
    # Add user message to history
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.chat_history.append({
        'role': 'user',
        'content': query,
        'timestamp': timestamp
    })
    
    # Prepare context
    context = {}
    if current_data:
        context['current_data'] = current_data
    
    # Call copilot API
    try:
        with st.spinner("🤔 Thinking..."):
            result = api_client._post("/copilot/query", {
                'query': query,
                'context': context if context else None
            })
        
        if result.get('success'):
            # Add assistant response to history
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': result['answer'],
                'timestamp': timestamp,
                'confidence': result.get('confidence'),
                'query_type': result.get('query_type')
            })
        else:
            st.error("Failed to get response from copilot")
    
    except Exception as e:
        st.error(f"Error: {e}")


def render_quick_actions(api_client, current_data: Optional[Dict]):
    """
    Render quick action buttons for common queries
    
    Args:
        api_client: API client instance
        current_data: Current process data
    """
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Root Cause Analysis", use_container_width=True):
            if current_data:
                with st.spinner("Analyzing..."):
                    result = api_client._post("/copilot/root-cause", {
                        'process_data': current_data,
                        'batch_id': current_data.get('batch_id', 'unknown')
                    })
                
                if result.get('success'):
                    st.markdown("#### Root Cause Analysis")
                    st.markdown(result['explanation'])
                    
                    if result.get('root_causes'):
                        st.markdown("**Identified Issues:**")
                        for cause in result['root_causes']:
                            severity_color = "#dc3545" if cause['severity'] == 'SEVERE' else "#ffc107"
                            st.markdown(
                                f"- **{cause['parameter']}**: {cause['current_value']:.2f} "
                                f"(Expected: {cause['expected_range']}) "
                                f"<span style='color:{severity_color};font-weight:bold;'>{cause['severity']}</span>",
                                unsafe_allow_html=True
                            )
            else:
                st.warning("Generate data first")
    
    with col2:
        if st.button("💡 Get Recommendations", use_container_width=True):
            if current_data:
                with st.spinner("Generating recommendations..."):
                    result = api_client._post("/copilot/optimize", {
                        'process_data': current_data,
                        'batch_id': current_data.get('batch_id', 'unknown'),
                        'target_status': 'GOOD'
                    })
                
                if result.get('success'):
                    st.markdown("#### Optimization Recommendations")
                    st.markdown(result['explanation'])
            else:
                st.warning("Generate data first")
    
    with col3:
        if st.button("📊 View History", use_container_width=True):
            with st.spinner("Loading..."):
                result = api_client._get("/copilot/interactions/recent", params={'limit': 10})
            
            if result.get('success'):
                st.markdown("#### Recent Interactions")
                interactions = result.get('interactions', [])
                
                if interactions:
                    for interaction in interactions[:5]:
                        with st.expander(f"Q: {interaction['query'][:50]}..."):
                            st.markdown(f"**Query**: {interaction['query']}")
                            st.markdown(f"**Response**: {interaction['response'][:200]}...")
                            st.caption(f"Type: {interaction['query_type']} | Confidence: {interaction['confidence']:.1%}")
                else:
                    st.info("No interaction history yet")


def render_copilot_stats(api_client):
    """
    Render copilot usage statistics
    
    Args:
        api_client: API client instance
    """
    try:
        result = api_client._get("/copilot/statistics")
        
        if result.get('success'):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Interactions",
                    result.get('total_interactions', 0)
                )
            
            with col2:
                st.metric(
                    "Avg Confidence",
                    f"{result.get('average_confidence', 0):.1%}"
                )
            
            with col3:
                query_types = result.get('query_type_distribution', {})
                most_common = max(query_types.items(), key=lambda x: x[1])[0] if query_types else "N/A"
                st.metric(
                    "Most Common Query",
                    most_common
                )
    
    except Exception as e:
        st.error(f"Failed to load statistics: {e}")


if __name__ == "__main__":
    # Test chat interface
    st.set_page_config(page_title="Chat Copilot Test", layout="wide")
    
    st.title("Chat Copilot Component Test")
    
    # Mock API client
    class MockAPIClient:
        def _post(self, endpoint, data):
            return {
                'success': True,
                'answer': "This is a test response from the copilot.",
                'confidence': 0.85,
                'query_type': 'test'
            }
        
        def _get(self, endpoint, params=None):
            return {
                'success': True,
                'interactions': [],
                'total_interactions': 0,
                'average_confidence': 0.0
            }
    
    mock_client = MockAPIClient()
    
    # Test data
    test_data = {
        'batch_id': 'TEST123',
        'die_temperature': 195.0,
        'wire_pull_strength': 5.0,
        'predicted_status': 'SEVERE'
    }
    
    # Render interface
    render_chat_interface(mock_client, test_data)
    
    st.markdown("---")
    render_quick_actions(mock_client, test_data)
    
    st.markdown("---")
    render_copilot_stats(mock_client)

# Made with Bob
