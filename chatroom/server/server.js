const io = require("socket.io")(3500, {
  cors: {
    origin: ["http://localhost:3000"],
  },
});
const { Kafka } = require("kafkajs");

const kafka_producer = new Kafka({
  clientId: "ss-mediator",
  brokers: ["pkc-lzvrd.us-west4.gcp.confluent.cloud:9092"],
  ssl: true,
  logLevel: 2,
  sasl: {
    mechanism: "plain", // scram-sha-256 or scram-sha-512
    username: "OKT6NPKMHWF2Q35E",
    password:
      "PX51AyMadxUMHRkM2CT+POD0n7OW1k2SXSOYpz1kXMoqDadr5Jr/oHH0YFcP2mnb",
  },
});

const kafka_consumer = new Kafka({
  clientId: "ss-client",
  brokers: ["pkc-lzvrd.us-west4.gcp.confluent.cloud:9092"],
  ssl: true,
  logLevel: 2,
  groupId: "ss-consumer",
  sasl: {
    mechanism: "plain", // scram-sha-256 or scram-sha-512
    username: "7ELFNKFFNBRYAGCD",
    password:
      "zXCGOM9BKXWeCQoioRDYzx6daKPo3vFh1PoK3ZHc0wYdBluUZEPnKMm/3bijwmP5",
  },
});

const producer = kafka_producer.producer();
const consumer = kafka_consumer.consumer({ groupId: "ss-chatroom-client" });

const connectProducer = async () => {
  try {
    await producer.connect();
    console.log("Producer Successfuly Connected");
  } catch (e) {
    console.log(e);
  }
};

const consumeMessages = async () => {
  try {
    console.log("waiting to consume");
    consumer.run({
      eachMessage: async ({ topic, message }) => {
        try {
          const res = JSON.parse(message.value.toString());
          console.log("---Consumed---");
          console.log(message.value.toString());
          console.log(res);
          const socket = io.sockets.sockets.get(res.from);
          socket.broadcast.emit("recieve-message", res);
        } catch (e) {}
      },
    });
  } catch (e) {
    console.log(e);
    // consumeMessages();
  }
};

const connectConsumer = async () => {
  try {
    await consumer.connect();
    await consumer.subscribe({ topics: ["flagged-queue", "clean-queue"] });
    console.log("Consumer Successfuly Connected");
    consumeMessages();
  } catch (e) {
    console.log(e);
  }
};

// Connect to the confluent broker
connectProducer();
connectConsumer();

const produceMessage = async (message) => {
  await producer.send({
    topic: "mediate-queue",
    messages: [{ value: message }],
  });
  console.log("sent message");
};

io.on("connection", (socket) => {
  socket.on("send-message", (message) => {
    produceMessage(JSON.stringify(message));
    console.log(message);
  });
});
