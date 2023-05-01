const io = require("socket.io")(3500, {
  cors: {
    origin: ["http://localhost:3000"],
  },
});

io.on("connection", (socket) => {
  console.log(socket.id);
  socket.on("send-message", (message) => {
    socket.broadcast.emit("recieve-message", message);
    console.log(message);
  });
});
