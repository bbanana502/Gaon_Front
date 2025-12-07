document.addEventListener('DOMContentLoaded', () => {
    const messagesArea = document.getElementById('messagesArea');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const newChatBtn = document.getElementById('newChatBtn');
    const historyList = document.getElementById('historyList');

    // Load history from local storage
    let chatHistory = JSON.parse(localStorage.getItem('gaonChangeHistory')) || [];

    // Initialize with a welcome message if empty
    if (chatHistory.length === 0) {
        addMessage('ai', 'Hello! I am Gaon AI. How can I help you today?');
    } else {
        renderHistory();
    }

    // Auto-scroll to bottom
    scrollToBottom();

    // Send Message Logic
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // New Chat Logic (Clear View - In a real app this might archive the session)
    newChatBtn.addEventListener('click', () => {
        if (confirm('Start a new chat? This will clear the current view (history is saved locally in list).')) {
            localStorage.removeItem('gaonChangeHistory');
            messagesArea.innerHTML = '';
            addMessage('ai', 'Hello! I am Gaon AI. How can I help you today?');
            chatHistory = [];
        }
    });

    function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Add User Message
        addMessage('user', text);
        chatInput.value = '';

        // Simulate AI Response
        setTimeout(() => {
            const response = generateMockResponse(text);
            addMessage('ai', response);
        }, 1000);
    }

    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        
        const avatarDiv = document.createElement('div');
        avatarDiv.classList.add('avatar');
        avatarDiv.textContent = sender === 'ai' ? 'G' : 'U';

        const textDiv = document.createElement('div');
        textDiv.classList.add('text');
        textDiv.textContent = text;

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(textDiv);
        messagesArea.appendChild(messageDiv);

        // Save to history
        chatHistory.push({ sender, text });
        localStorage.setItem('gaonChangeHistory', JSON.stringify(chatHistory));
        
        scrollToBottom();
    }

    function renderHistory() {
        chatHistory.forEach(msg => {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', `${msg.sender}-message`);
            
            const avatarDiv = document.createElement('div');
            avatarDiv.classList.add('avatar');
            avatarDiv.textContent = msg.sender === 'ai' ? 'G' : 'U';

            const textDiv = document.createElement('div');
            textDiv.classList.add('text');
            textDiv.textContent = msg.text;

            messageDiv.appendChild(avatarDiv);
            messageDiv.appendChild(textDiv);
            messagesArea.appendChild(messageDiv);
        });
    }

    function scrollToBottom() {
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }

    function generateMockResponse(input) {
        const lowerInput = input.toLowerCase();
        if (lowerInput.includes('hello') || lowerInput.includes('hi')) return "Hello there! How's your schedule looking?";
        if (lowerInput.includes('schedule') || lowerInput.includes('plan')) return "I can help you manage your plans. Would you like to add a new event?";
        if (lowerInput.includes('thank')) return "You're welcome!";
        return "I'm just a demo AI, but I'm listening! Tell me more.";
    }
});
