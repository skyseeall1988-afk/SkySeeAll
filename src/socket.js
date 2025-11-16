import { io } from 'socket.io-client';

// Use window.location.origin for production compatibility
const URL = window.location.origin;

export const socket = io(URL, {
    autoConnect: false
});
