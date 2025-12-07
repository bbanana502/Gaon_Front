document.addEventListener('DOMContentLoaded', () => {
    const messagesArea = document.getElementById('messagesArea');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const newChatBtn = document.getElementById('newChatBtn');
    const historyList = document.getElementById('historyList');

    // Data Store
    let sessions = JSON.parse(localStorage.getItem('gaonChatSessions')) || [];
    let currentSessionId = null;

    // Initialize: Load last session or create new
    if (sessions.length > 0) {
        loadSession(sessions[0].id);
    } else {
        startNewChat();
    }

    renderHistory();

    // Scroll to bottom
    scrollToBottom();

    // Event Listeners
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    newChatBtn.addEventListener('click', () => {
        startNewChat();
    });

    // --- Core Functions ---

    function startNewChat() {
        // Create new session
        const newSession = {
            id: Date.now().toString(),
            title: "새로운 대화",
            messages: [{ sender: 'ai', text: '안녕하세요! 가온 AI입니다. 무엇을 도와드릴까요?' }]
        };
        
        sessions.unshift(newSession); // Add to top
        saveSessions();
        renderHistory();
        loadSession(newSession.id);
    }

    function loadSession(id) {
        currentSessionId = id;
        const session = sessions.find(s => s.id === id);
        if (!session) return;

        // Render Messages
        messagesArea.innerHTML = '';
        
        // Use a fragment for performance if many messages, but for now simple loop
        session.messages.forEach(msg => {
            renderMessageBubble(msg.sender, msg.text);
        });
        
        scrollToBottom();
        renderHistory(); // Update active state
    }

    function renderHistory() {
        historyList.innerHTML = '';
        sessions.forEach(session => {
            const item = document.createElement('div');
            item.className = `history-item ${session.id === currentSessionId ? 'active' : ''}`;
            item.textContent = session.title;
            item.onclick = () => loadSession(session.id);
            historyList.appendChild(item);
        });
    }

    function saveSessions() {
        localStorage.setItem('gaonChatSessions', JSON.stringify(sessions));
    }

    // --- Message Handling ---

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Add User Message
        addMessage('user', text);
        chatInput.value = '';
        
        // Loading UI
        chatInput.disabled = true;
        sendBtn.disabled = true;
        const loadingId = renderMessageBubble('ai', '...', true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();
            
            // Remove loading bubble
            const loadingEl = document.querySelector(`.message[data-id="${loadingId}"]`);
            if (loadingEl) loadingEl.remove();

            // Add real response
            addMessage('ai', data.response);
            
        } catch (error) {
            console.error('Chat Error:', error);
            const loadingEl = document.querySelector(`.message[data-id="${loadingId}"]`);
            if (loadingEl) loadingEl.remove(); // Clean up loading explicitly
            addMessage('ai', '오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
        } finally {
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
        }
    }

    function addMessage(sender, text) {
        // 1. Update Data
        const session = sessions.find(s => s.id === currentSessionId);
        if (session) {
            session.messages.push({ sender, text });
            
            // Update Title if it's the first user message (or 2nd msg total, after welcome)
            if (sender === 'user' && session.messages.length <= 2) {
                session.title = text.length > 20 ? text.substring(0, 20) + '...' : text;
            }
            saveSessions();
            renderHistory(); // Update title in sidebar
        }

        // 2. Render UI
        renderMessageBubble(sender, text);
    }

    // Low-level render function (UI only)
    function renderMessageBubble(sender, text, isLoading = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        const msgId = Date.now().toString() + Math.random().toString();
        messageDiv.dataset.id = msgId;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.classList.add('avatar');
        avatarDiv.textContent = sender === 'ai' ? '🤖' : '👤';

        const textDiv = document.createElement('div');
        textDiv.classList.add('text');
        
        if (isLoading) {
            textDiv.innerHTML = '<span class="loading-dots"></span>';
        } else {
            textDiv.innerHTML = text.replace(/\n/g, '<br>');
        }

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(textDiv);
        messagesArea.appendChild(messageDiv);
        
        scrollToBottom();
        return msgId;
    }

    function scrollToBottom() {
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }
});
