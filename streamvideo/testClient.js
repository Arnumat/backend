const socket = new WebSocket('ws://127.0.0.1:8000/ws/video_stream/');

socket.onopen = function() {
    socket.send(JSON.stringify({ type: 'test.message', content: 'Hello, world!' }));
};

socket.onmessage = function(event) {
    console.log('Message from server ', event.data);
};
