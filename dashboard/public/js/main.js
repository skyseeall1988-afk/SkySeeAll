
const term = new Terminal();
const fitAddon = new FitAddon.FitAddon();
term.loadAddon(fitAddon);
term.open(document.getElementById('terminal'));
fitAddon.fit();

const ws = new WebSocket(`ws://${location.host}/shell`);

ws.onopen = () => {
    console.log('WebSocket connection opened');
};

ws.onmessage = (event) => {
    term.write(event.data);
};

ws.onclose = () => {
    console.log('WebSocket connection closed');
};

term.onData((data) => {
    ws.send(data);
});
