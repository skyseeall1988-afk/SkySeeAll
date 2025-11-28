
const express = require('express');
const expressWs = require('express-ws');
const pty = require('node-pty');
const os = require('os');

const app = express();
expressWs(app);

const shell = os.platform() === 'win32' ? 'powershell.exe' : 'bash';

app.use(express.static(__dirname + '/public'));

app.ws('/shell', (ws, req) => {
    const term = pty.spawn(shell, [], {
        name: 'xterm-color',
        cols: 80,
        rows: 30,
        cwd: process.env.HOME,
        env: process.env
    });

    term.on('data', (data) => {
        ws.send(data);
    });

    ws.on('message', (msg) => {
        term.write(msg);
    });

    ws.on('close', () => {
        term.kill();
    });
});

const port = 3000;
app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});
