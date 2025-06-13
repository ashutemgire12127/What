const socket = io();
const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message');

let username = prompt('Enter your username:');
if (!username) username = 'Anonymous';
socket.emit('join', { username, room: 'main' });

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (!message) return;

    socket.emit('message', { username, message });
    messageInput.value = '';
});

socket.on('message', (data) => {
    const messageElement = document.createElement('div');
    messageElement.textContent = `${data.username}: ${data.message}`;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
});