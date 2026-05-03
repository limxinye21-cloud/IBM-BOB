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
    """
    # Inject chat-specific styles
    st.markdown("""
    <style>
    .chat-wrap  { max-height:480px; overflow-y:auto; padding:4px 0; }
    .msg-user   { display:flex; justify-content:flex-end; margin:8px 0; }
    .msg-bot    { display:flex; justify-content:flex-start; margin:8px 0; }
    .bubble-user{
        background:linear-gradient(135deg,#0f62fe,#0043ce);
        color:white; padding:12px 16px; border-radius:18px 18px 4px 18px;
        max-width:72%; font-size:14px; line-height:1.5;
        box-shadow:0 2px 8px rgba(15,98,254,.25);
    }
    .bubble-bot {
        background:white;
        color:#1a2238; padding:12px 16px; border-radius:18px 18px 18px 4px;
        max-width:75%; font-size:13.5px; line-height:1.6;
        border-left:3px solid #0f62fe;
        box-shadow:0 2px 10px rgba(15,98,254,.12);
    }
    .bot-header { font-weight:700; color:#0043ce; margin-bottom:6px; font-size:13px; }
    .badge      { display:inline-block; padding:2px 8px; border-radius:10px;
                  font-size:11px; font-weight:600; margin-left:6px; }
    .badge-conf { background:#ddeeff; color:#0043ce; }
    .badge-type { background:#eef2ff; color:#697077; }
    .ts         { font-size:10px; opacity:.45; margin-top:5px; }
    .chip-row   { display:flex; flex-wrap:wrap; gap:6px; margin:8px 0; }
    .chip {
        background:#e8f0ff; color:#0043ce; border:1px solid #0f62fe33;
        padding:5px 12px; border-radius:20px; font-size:12px; cursor:pointer;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### 💬 AI Copilot Chat")
    st.caption("Ask about process status, root causes, recommendations, or forecasts.")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # --- Suggested quick queries (only when no history) ---
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="chip-row">
            <span class="chip">🔍 Why is this severe?</span>
            <span class="chip">📈 Show process health</span>
            <span class="chip">🔮 Forecast next 5 cycles</span>
            <span class="chip">💡 Optimize parameters</span>
        </div>
        """, unsafe_allow_html=True)
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            if st.button("🔍 Why is this batch severe?", use_container_width=True):
                process_query("Why is this batch severe?", api_client, current_data)
            if st.button("📊 Show process health", use_container_width=True):
                process_query("Show process health", api_client, current_data)
        with col_q2:
            if st.button("🔮 Forecast next 5 cycles", use_container_width=True):
                process_query("Forecast next 5 cycles", api_client, current_data)
            if st.button("💡 Optimize parameters", use_container_width=True):
                process_query("How can I optimize this process?", api_client, current_data)
    else:
        # Chat history
        for message in st.session_state.chat_history:
            render_chat_message(message)

        # Suggested follow-ups after last bot message
        last_bot = next((m for m in reversed(st.session_state.chat_history) if m.get('role') == 'assistant'), None)
        if last_bot:
            qtype = last_bot.get('query_type', '')
            follow_ups = {
                'why':            ["Show recommendations", "Forecast next 5 cycles", "Analyze all stages"],
                'health':         ["Why is the score low?", "Forecast next 5 cycles", "Show recommendations"],
                'forecast':       ["What are root causes?", "How to optimize?", "Analyze wire bonding"],
                'recommendation': ["Why these recommendations?", "Show process health", "Forecast"],
            }.get(qtype, ["Show process health", "Why is this severe?", "Suggest optimization"])

            st.markdown('<div class="chip-row">' +
                        ''.join(f'<span class="chip">{q}</span>' for q in follow_ups[:3]) +
                        '</div>', unsafe_allow_html=True)
            f_cols = st.columns(len(follow_ups[:3]))
            for i, fq in enumerate(follow_ups[:3]):
                with f_cols[i]:
                    if st.button(fq, key=f"fup_{i}", use_container_width=True):
                        process_query(fq, api_client, current_data)
                        st.rerun()

    # Input row
    st.markdown("---")
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Your question:",
            key="chat_input",
            placeholder="Ask about process health, root causes, forecasts...",
            label_visibility="collapsed"
        )
    with col2:
        send_button = st.button("➤ Send", use_container_width=True)

    if send_button and user_input:
        process_query(user_input, api_client, current_data)
        st.rerun()

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
        st.markdown(
            f'<div class="msg-user">'
            f'<div class="bubble-user">'
            f'{content}'
            f'<div class="ts">{timestamp}</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )
    else:
        confidence_badge = ""
        if confidence is not None:
            conf_pct = confidence * 100
            badge_cls = 'badge-conf'
            confidence_badge = f'<span class="badge {badge_cls}">{conf_pct:.0f}% confident</span>'
        type_badge = f'<span class="badge badge-type">{query_type}</span>' if query_type else ""

        st.markdown(
            f'<div class="msg-bot">'
            f'<div class="bubble-bot">'
            f'<div class="bot-header">🤖 IBM BOB {confidence_badge} {type_badge}</div>'
            f'<div>{content}</div>'
            f'<div class="ts">{timestamp}</div>'
            f'</div></div>',
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
