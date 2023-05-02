import * as React from "react";
import { styled, withTheme } from "@mui/material/styles";
import ArrowForwardIosSharpIcon from "@mui/icons-material/ArrowForwardIosSharp";
import MuiAccordion, { AccordionProps } from "@mui/material/Accordion";
import MuiAccordionSummary, {
  AccordionSummaryProps,
} from "@mui/material/AccordionSummary";
import MuiAccordionDetails from "@mui/material/AccordionDetails";
import Typography from "@mui/material/Typography";
import { Button, Grid } from "@mui/material";
import WarningIcon from "@mui/icons-material/Warning";
import DashCard from "./DashCard";

const Accordion = styled((props: AccordionProps) => (
  <MuiAccordion disableGutters elevation={0} square {...props} />
))(({ theme }) => ({
  flex: "1 1 auto",
  backgroundColor: "rgba(0, 0, 0, 0)",
  "&:not(:last-child)": {
    borderBottom: 0,
  },
  "&:before": {
    display: "none",
  },
}));

const AccordionSummary = styled((props: AccordionSummaryProps) => (
  <MuiAccordionSummary
    expandIcon={<ArrowForwardIosSharpIcon sx={{ fontSize: "0.9rem" }} />}
    {...props}
  />
))(({ theme }) => ({
  borderRadius: "8px",
  boxShadow: "1px 2px 5px #e8e8e8 !important",
  backgroundColor:
    theme.palette.mode === "dark"
      ? "#272727"
      : `${theme.palette.background.paper}`,
  flexDirection: "row",
  "& .MuiAccordionSummary-expandIconWrapper.Mui-expanded": {
    transform: "rotate(90deg)",
  },
  "& .MuiAccordionSummary-content": {
    marginLeft: theme.spacing(1),
  },
}));

const AccordionDetails = styled(MuiAccordionDetails)(({ theme }) => ({
  padding: theme.spacing(1, 0.5, 0.5, 0.5),
  backgroundColor: "rgba(0, 0, 0, 0)",
  // uncomment to make accordions stationary
  // maxHeight: "80vh",
  overflow: "scroll",
}));

// : "350px",
// :"500px",
export default function DashAccordion({
  message,
  minWidth,
  maxWidth,
  ...props
}: {
  message?: string;
  minWidth?: string;
  maxWidth?: string;
}) {
  const [open, setOpen] = React.useState(false);
  const [display, setDisplay] = React.useState("block");

  const handleClose = (event: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    setOpen(!open);
  };

  const [expanded, setExpanded] = React.useState<string | false>("");

  const handleChange =
    (panel: string) => (event: React.SyntheticEvent, newExpanded: boolean) => {
      setExpanded(newExpanded ? panel : false);
    };

  const handleInappropriate = () => {
    setDisplay("none");
  };

  const handleAppropriate = () => {};

  return (
    <Grid
      display={display}
      container
      justifyContent={"center"}
      padding={0.5}
      sx={{ height: "100%" }}
    >
      <Accordion
        expanded={expanded === "panel1"}
        onChange={handleChange("panel1")}
      >
        <AccordionSummary
          aria-controls="panel1d-content"
          id="panel1d-header"
          expandIcon={<></>}
        >
          <Grid container alignItems={"center"}>
            <WarningIcon
              sx={{
                mr: 2,
                color: "orange",
              }}
            />
            <Grid item sx={{ flex: "1 1 auto" }}>
              <Typography variant="body2" sx={{ color: "black" }}>
                Parental Supervision Reqired
              </Typography>
            </Grid>
            <Button>review</Button>
          </Grid>
        </AccordionSummary>
        <AccordionDetails>
          <DashCard color="#ffdec4">
            <Grid container>
              <Grid item xs={12} sx={{ pt: 1, pb: 1 }}>
                <Typography variant="subtitle2">Message: {message}</Typography>
              </Grid>
              <Grid container alignItems={"center"}>
                <Grid item xs={8}>
                  <Typography variant="body2" sx={{ fontStyle: "italic" }}>
                    is this message inappropriate?
                  </Typography>
                </Grid>
                <Grid item xs={2}>
                  <Button
                    sx={{ m: 0, fontSize: "13px" }}
                    onClick={() => handleInappropriate()}
                  >
                    yes
                  </Button>
                </Grid>
                <Grid item xs={2}>
                  <Button
                    sx={{ m: 0, fontSize: "13px" }}
                    onClick={() => handleAppropriate()}
                  >
                    no
                  </Button>
                </Grid>
              </Grid>
            </Grid>
          </DashCard>
        </AccordionDetails>
      </Accordion>
    </Grid>
  );
}
