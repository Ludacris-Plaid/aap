function sendMessage() {
    const input = document.getElementById('msg');
    const chatBox = document.getElementById('chat-box');
    if (input.value.trim() !== '') {
        const msg = document.createElement('div');
        msg.textContent = input.value;
        chatBox.appendChild(msg);
        input.value = '';
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}
