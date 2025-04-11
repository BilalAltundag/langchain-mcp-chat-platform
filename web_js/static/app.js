document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chatContainer');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const commandBubbles = document.querySelectorAll('.command-bubble');

    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'} fade-in`;
        messageDiv.textContent = content;
        chatContainer.appendChild(messageDiv);
        
        // Trigger reflow for animation
        messageDiv.offsetHeight;
        messageDiv.classList.remove('fade-in');
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = '<span></span><span></span><span></span>';
        chatContainer.appendChild(indicator);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return indicator;
    }

    async function sendMessage(message) {
        if (!message.trim()) return;

        // Add user message
        addMessage(message, true);
        messageInput.value = '';

        // Show typing indicator
        const typingIndicator = showTypingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            
            // Remove typing indicator
            typingIndicator.remove();
            
            // Add assistant response
            addMessage(data.response);

        } catch (error) {
            console.error('Error:', error);
            typingIndicator.remove();
            addMessage('Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.', false);
        }
    }

    // Event listeners
    sendButton.addEventListener('click', () => {
        sendMessage(messageInput.value);
    });

    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage(messageInput.value);
        }
    });

    commandBubbles.forEach(bubble => {
        bubble.addEventListener('click', () => {
            const command = bubble.textContent;
            messageInput.value = command;
            sendMessage(command);
        });
    });
}); 