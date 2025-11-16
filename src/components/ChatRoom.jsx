import React, { useState, useEffect } from 'react';

export const ChatRoom = ({ socket, username, room }) => {
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState();

    useEffect(() => {
        if (socket && username && room) {
            socket.emit('join', { username, room });
            
            const handleMessage = (msg) => {
                setMessages((prevMessages) => [...prevMessages, msg]);
            };

            socket.on('message', handleMessage);
            
            return () => {
                socket.emit('leave', { username, room });
                socket.off('message', handleMessage);
            };
        }
    }, [socket, username, room]);

    const sendMessage = (e) => {
        e.preventDefault();
        if (message && socket) {
            socket.emit('message', { user: username, text: message, room });
            setMessage('');
        }
    };

    return (
        <div className="bg-white p-4 rounded-xl shadow-lg h-96 flex flex-col">
            <h3 className="text-lg font-semibold border-b pb-2">V10 Chat Room: {room}</h3>
            <div className="flex-grow overflow-y-auto space-y-2 my-2 p-2 bg-gray-100 rounded">
                {messages.map((msg, index) => (
                    <div key={index} className="text-sm">
                        <strong className="text-blue-600">{msg.user}:</strong> <span>{msg.text}</span>
                    </div>
                ))}
            </div>
            <form onSubmit={sendMessage} className="flex gap-2">
                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type a message..."
                    className="flex-grow p-2 border rounded-lg"
                />
                <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded-lg">Send</button>
            </form>
        </div>
    );
};
