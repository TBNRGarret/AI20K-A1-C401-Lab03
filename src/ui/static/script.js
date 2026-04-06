const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const thinkingOverlay = document.getElementById('thinking-overlay');

/**
 * Thêm tin nhắn vào khung chat
 */
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    
    // Bubble effect
    messageDiv.innerHTML = `
        <div class="bubble">
            ${text}
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Hiện bong bóng "đang soạn tin"
 */
function showTyping() {
    const typingDiv = document.createElement('div');
    typingDiv.classList.add('message', 'bot', 'typing-msg');
    typingDiv.innerHTML = `
        <div class="bubble">
            <div class="typing-indicator">
                <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return typingDiv;
}

/**
 * Gửi tin nhắn tới Server
 */
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    userInput.value = '';
    addMessage(message, 'user');

    // Hiện "Agent đang soạn tin..."
    const typingBubble = showTyping();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        // Xóa bong bóng typing
        typingBubble.remove();

        if (data.status === 'success') {
            addMessage(data.answer, 'bot');
        } else {
            addMessage('❌ Lỗi Agent: ' + (data.error || 'Agent không phản hồi.'), 'bot');
        }
    } catch (err) {
        typingBubble.remove();
        addMessage('❌ Lỗi kết nối: ' + err.message, 'bot');
        console.error(err);
    }
}

// Event Listeners
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

const resetBtn = document.getElementById('reset-btn');
resetBtn.addEventListener('click', async () => {
    if (!confirm("Bạn có chắc chắn muốn xóa toàn bộ lịch sử tư vấn không?")) return;
    
    try {
        const response = await fetch('/reset', { method: 'POST' });
        if (response.ok) {
            chatMessages.innerHTML = `
                <div class="message bot intro">
                    <div class="bubble">
                        Lịch sử đã được xóa. Mình đã sẵn sàng cho cuộc trò chuyện mới!
                    </div>
                </div>
            `;
            console.log("Chat history has been reset.");
        }
    } catch (err) {
        console.error("Lỗi khi reset chat:", err);
    }
});
