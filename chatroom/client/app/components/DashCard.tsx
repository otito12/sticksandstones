import { Card, Grid, Typography, useTheme } from "@mui/material";
import * as React from "react";

export default function DashCard({
  title,
  toolTip,
  boxShadow,
  children,
  color,
  aspectRatio,
  maxWidth,
}: {
  title?: string;
  toolTip?: string;
  color?: string;
  children?: React.ReactNode;
  aspectRatio?: string;
  boxShadow?: string;
  maxWidth?: string;
}) {
  const theme = useTheme();
  return (
    <Grid
      container
      justifyContent={"center"}
      padding={0.5}
      sx={{ height: "100%" }}
    >
      <Card
        elevation={2}
        sx={{
          background: `${color}`,
          boxShadow: `${
            boxShadow ? boxShadow : "1px 5px 10px #e8e8e8 !important"
          }`,
          borderRadius: "8px",
          width: "100%",
          maxWidth: `${maxWidth ? maxWidth : "None"}`,
        }}
      >
        {/* Forces the card to be in 1/1 aspect ratio  */}

        <Grid
          container
          justifyContent={"center"}
          alignItems={"center"}
          sx={{
            width: "100%",
            height: "100%",
            padding: "16px",
          }}
        >
          <Grid
            container
            direction="column"
            alignItems={"center"}
            sx={{
              width: "100%",
              height: "100%",
            }}
          >
            <Grid item sx={{ width: "100%" }}>
              {(title || toolTip) && (
                <Grid container justifyContent={"start"} alignContent={"end"}>
                  <Typography
                    variant="body1"
                    sx={{ color: `${theme.palette.text.primary}` }}
                  >
                    {title}
                  </Typography>
                </Grid>
              )}
            </Grid>
            {children && (
              <Grid
                container
                alignContent={"center"}
                sx={{
                  width: "100%",
                  flex: "1 1 auto",
                }}
              >
                {children}
              </Grid>
            )}
          </Grid>
        </Grid>
      </Card>
    </Grid>
  );
}
