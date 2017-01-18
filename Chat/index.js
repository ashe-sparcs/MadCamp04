/**
 * Created by Madstein on 2017-01-19.
 */
var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);

io.on('connection', function(socket){
    socket.on('chat message', function (data) {
        io.in(data.id).emit('chat message', data.message);
    });
    socket.on('joinRoom', function (data) {
        socket.join(data.id);
        io.in(data.id).emit('notification', data.username + ' has connected.');
    });
});

http.listen(3000, function(){
    console.log('listening on *:3000');
});