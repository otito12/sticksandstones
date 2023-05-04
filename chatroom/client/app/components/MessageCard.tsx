import { Box, Button, Grid, Typography } from "@mui/material";
import React from "react";
import DashCard from "./DashCard";
import MessageSensor from "./MessageSensor";
import { Message } from "../../typings";
import { useState } from "react";

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
  const [mesFlag, setMesFlag] = useState(flagged);
  return (
    <Grid container alignItems={"end"}>
      {sent && <Grid item sx={{ flex: "1 1 auto" }}></Grid>}
      <Grid item xs={5} sx={{ minWidth: "350px" }}>
        {!mesFlag ? (
          <DashCard color={sent ? "#1976d2" : "white"}>
            <Typography
              variant="body2"
              sx={{ color: `${sent ? "white" : "black"}` }}
            >
              {message ? message : ""}
            </Typography>
          </DashCard>
        ) : (
          <MessageSensor message={message} setFlag={setMesFlag} />
        )}
      </Grid>
    </Grid>
  );
}
