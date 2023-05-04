"use client";
import React, { useEffect, useRef } from "react";
import { Socket, io } from "socket.io-client";
import DashCard from "./components/DashCard";
import SendIcon from "@mui/icons-material/Send";
import {
  Button,
  FormControl,
  Grid,
  InputLabel,
  OutlinedInput,
  Paper,
  Typography,
} from "@mui/material";
import { useState } from "react";
import { DefaultEventsMap } from "@socket.io/component-emitter";
import { Message } from "../typings";
import MessageCard from "./components/MessageCard";

export default function ChatRoom() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [current_message, set_current_message] = useState("");
  const [loading, setLoading] = useState(true);
  const [socket, setSocket] =
    useState<Socket<DefaultEventsMap, DefaultEventsMap>>();

  useEffect(() => {
    // setSocket(io("http://localhost:3500"));
    setSocket(io("http://127.0.0.1:5001"));
  }, []);

  socket?.on("connect", () => {
    setLoading(false);
  });

  socket?.on("recieve-message", (message) => {
    setMessages([...messages, message]);
  });

  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleMessageSend = (event: any) => {
    event.preventDefault();
    if (current_message.length > 0) {
      let message: Message = {
        from: socket!.id,
        to: "*",
        sent: Date.now(),
        message: current_message,
        flagged: false,
      };
      setMessages([...messages, message]);
      socket!.emit("send-message", message);
      set_current_message("");
    }
  };

  const onChangeMessage = (event: any) => {
    event.preventDefault();
    set_current_message(event.target.value);
    console.log(current_message);
  };

  return (
    <Grid container sx={{ height: "95vh" }} alignItems={"flex-start"}>
      <DashCard title={`Welcome to Sticks & Stones Chatroom`}>
        {!loading && (
          //
          <>
            {/* Message Display Container */}
            <Grid container sx={{ mt: 1, mb: 1 }}>
              <Paper
                elevation={0}
                sx={{
                  height: "70vh",
                  maxHeight: "70vh",
                  overflow: "scroll",
                  width: "100%",
                  background: "#f5f5f5",
                  p: 2,
                  mb: 2,
                }}
              >
                {messages.length > 0 &&
                  messages.map((message) => (
                    <MessageCard
                      messageObj={message}
                      message={message.message}
                      sent={message.from === socket!.id}
                      flagged={message.flagged}
                    />
                  ))}
                <div ref={messagesEndRef} />
              </Paper>
            </Grid>
            {/* Message Form Container */}
            <Grid container sx={{ width: "100%" }}>
              <form style={{ width: "100%" }} onSubmit={handleMessageSend}>
                <Grid container>
                  <Grid item xs={11} sx={{ pr: 1 }}>
                    <FormControl sx={{ width: "100%" }} variant="outlined">
                      <InputLabel htmlFor="standard-adornment-amount">
                        Message
                      </InputLabel>
                      <OutlinedInput
                        label="Message"
                        placeholder="Message"
                        name="message"
                        value={current_message}
                        onChange={onChangeMessage}
                      />
                    </FormControl>
                  </Grid>

                  <Grid item xs={1}>
                    <Grid
                      container
                      sx={{ width: "100%", height: "100%" }}
                      justifyContent={"center"}
                    >
                      <Button
                        sx={{ width: "100%", height: "100%" }}
                        disableElevation
                        disableRipple
                        color="primary"
                        variant="contained"
                        type="submit"
                      >
                        <SendIcon />
                      </Button>
                    </Grid>
                  </Grid>
                </Grid>
              </form>
            </Grid>
          </>
        )}
      </DashCard>
    </Grid>
  );
}
