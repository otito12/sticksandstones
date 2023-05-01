import { Box, Grid, Typography } from "@mui/material";
import React from "react";
import DashCard from "./DashCard";

export default function Message({
  message,
  sent,
}: {
  message?: string;
  sent: boolean;
}) {
  return (
    <Grid container alignItems={"end"}>
      {sent && <Grid item xs={8}></Grid>}
      <Grid item xs={4}>
        <DashCard color={sent ? "#1976d2" : "white"}>
          <Typography
            variant="body2"
            sx={{ color: `${sent ? "white" : "black"}` }}
          >
            {message ? message : ""}
          </Typography>
        </DashCard>
      </Grid>
    </Grid>
  );
}
