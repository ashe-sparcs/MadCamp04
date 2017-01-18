/**
 * Created by q on 2017-01-18.
 */
var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);


io.on('connection', function(socket) {
    console.log('user connected');
    socket.on('chat message', function (msg) {
        console.log('chat message : ' + msg);
        socket.emit('chat message', msg);
    });
    socket.on('join notification room', function (msg) {
        socket.join(msg.username);
    });
    socket.on('leave notification room', function (msg) {
        socket.leave(msg.username);
    });
    socket.on('join chat room', function (msg) {
        socket.join(msg.id);
    });
    socket.on('leave chat room', function (msg) {
        socket.leave(msg.id);
    });
});

http.listen(3000, function() {
    console.log('listening on port 3000');
});