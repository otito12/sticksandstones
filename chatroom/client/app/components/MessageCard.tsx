import { Box, Button, Grid, Typography } from "@mui/material";
import React from "react";
import DashCard from "./DashCard";
import MessageSensor from "./MessageSensor";
import { Message } from "../../typings";

export default function MessageCard({
  message,
  sent,
  flagged,
}: {
  messageObj: Message;
  message?: string;
  sent: boolean;
  flagged?: boolean;
}) {
  return (
    <Grid container alignItems={"end"}>
      {sent && <Grid item xs={8}></Grid>}
      <Grid item xs={4}>
        {!flagged ? (
          <DashCard color={sent ? "#1976d2" : "white"}>
            <Typography
              variant="body2"
              sx={{ color: `${sent ? "white" : "black"}` }}
            >
              {message ? message : ""}
            </Typography>
          </DashCard>
        ) : (
          <MessageSensor message={message} />
        )}
      </Grid>
    </Grid>
  );
}
