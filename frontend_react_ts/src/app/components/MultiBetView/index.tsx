/**
 *
 * MultiBetView
 *
 */
import * as React from 'react';
import { MultiBet, SingleBet } from 'types/Bet';
import { SingleBetView } from '../SingleBetView';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import Toolbar from '@mui/material/Toolbar';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Grid';
import { styled } from '@mui/material/styles';
import ArrowForwardIosSharpIcon from '@mui/icons-material/ArrowForwardIosSharp';
import MuiAccordion, { AccordionProps } from '@mui/material/Accordion';
import MuiAccordionSummary, {
  AccordionSummaryProps,
} from '@mui/material/AccordionSummary';
import MuiAccordionDetails from '@mui/material/AccordionDetails';

const Accordion = styled((props: AccordionProps) => (
  <MuiAccordion disableGutters elevation={0} square {...props} />
))(({ theme }) => ({
  border: `1px solid ${theme.palette.divider}`,
  '&:not(:last-child)': {
    borderBottom: 0,
  },
  '&:before': {
    display: 'none',
  },
}));

const AccordionSummary = styled((props: AccordionSummaryProps) => (
  <MuiAccordionSummary
    expandIcon={<ArrowForwardIosSharpIcon sx={{ fontSize: '0.9rem' }} />}
    {...props}
  />
))(({ theme }) => ({
  backgroundColor:
    theme.palette.mode === 'dark'
      ? 'rgba(255, 255, 255, .05)'
      : 'rgba(0, 0, 0, .03)',
  flexDirection: 'row-reverse',
  '& .MuiAccordionSummary-expandIconWrapper.Mui-expanded': {
    transform: 'rotate(90deg)',
  },
  '& .MuiAccordionSummary-content': {
    marginLeft: theme.spacing(1),
  },
}));

const AccordionDetails = styled(MuiAccordionDetails)(({ theme }) => ({
  padding: theme.spacing(2),
  borderTop: '1px solid rgba(0, 0, 0, .125)',
}));

function getBetShorthand(bet: SingleBet) {
  const entryShorthand = bet.active_entries
    .map(entry => `#${entry.program_no} ${entry.name}`)
    .join('; ');

  return `${bet.race.track_code.toUpperCase()} - ${
    bet.bet_type
  } - ${entryShorthand}`;
}

interface Props {
  bet: MultiBet;
}

export function MultiBetView({ bet }: Props) {
  const [expanded, setExpanded] = React.useState<string | false>(false);

  const handleChange =
    (panel: string) => (event: React.SyntheticEvent, newExpanded: boolean) => {
      setExpanded(newExpanded ? panel : false);
    };

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        {bet.sub_bets.map((bet, i) => (
          <Accordion
            key={`accordion-bet-${bet.id}`}
            expanded={expanded === `${bet.id}`}
            onChange={handleChange(`${bet.id}`)}
          >
            <AccordionSummary>
              <Typography>
                Bet {i + 1} - {getBetShorthand(bet)}
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <SingleBetView dense bet={bet} />
            </AccordionDetails>
          </Accordion>
        ))}
      </Grid>
      <Grid item xs={12}>
        <Paper sx={{ height: '100%' }}>
          <Toolbar
            sx={{
              pl: { sm: 2 },
              pr: { xs: 1, sm: 1 },
              minHeight: '3em !important',
              bgcolor: theme => theme.palette.primary.main,
              color: theme => theme.palette.primary.contrastText,
            }}
          >
            <Typography
              sx={{ flex: '1 1 100%' }}
              color="inherit"
              variant="subtitle1"
              component="div"
            >
              MultiBet Details
            </Typography>
          </Toolbar>
          <TableContainer component={Paper}>
            <Table size="small" aria-label="a dense table">
              <TableBody>
                <TableRow
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row">
                    Predicted Odds
                  </TableCell>
                  <TableCell align="right">{bet.predicted_odds}</TableCell>
                </TableRow>
                <TableRow
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row">
                    Min Reward
                  </TableCell>
                  <TableCell align="right">
                    ${bet.min_reward.toFixed(2)}
                  </TableCell>
                </TableRow>
                <TableRow
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row">
                    Avg. Reward
                  </TableCell>
                  <TableCell align="right">
                    ${bet.avg_reward.toFixed(2)}
                  </TableCell>
                </TableRow>
                <TableRow
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row">
                    Max Reward
                  </TableCell>
                  <TableCell align="right">
                    ${bet.max_reward.toFixed(2)}
                  </TableCell>
                </TableRow>
                <TableRow
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row">
                    Cost
                  </TableCell>
                  <TableCell align="right">${bet.cost.toFixed(2)}</TableCell>
                </TableRow>
                <TableRow
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row">
                    Bet Type
                  </TableCell>
                  <TableCell align="right">{bet.bet_type}</TableCell>
                </TableRow>
                <TableRow
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row">
                    Bet Strategy
                  </TableCell>
                  <TableCell align="right">{bet.bet_strategy_type}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </Grid>
    </Grid>
  );
}
