/**
 *
 * SingleBetView
 *
 */
import * as React from 'react';
import { SingleBet } from 'types/Bet';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import Toolbar from '@mui/material/Toolbar';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import { EntriesTable } from 'app/components/EntriesTable';
import { CountdownTimer } from '../CountdownTimer';
import { getEffectiveTS } from 'utils/bets';

interface Props {
  bet: SingleBet;
  dense?: boolean | null;
}

export function SingleBetView({ bet, dense = false }: Props) {
  return (
    <>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <EntriesTable defaultDense={dense} rows={bet.active_entries} title="Active Entries" />
        </Grid>
        <Grid item xs={12}>
          <EntriesTable defaultDense={dense} defaultExpanded={false} rows={bet.inactive_entries} title="Inactive Entries" />
        </Grid>
        <Grid item xl={6} md={12} xs={12}>
          <Paper>
            <Toolbar
              sx={{
                pl: { sm: 2 },
                pr: { xs: 1, sm: 1 },
                minHeight: '3em !important',
                ...{
                  bgcolor: theme => theme.palette.primary.main,
                  color: theme => theme.palette.primary.contrastText,
                },
              }}
            >
              <Typography
                sx={{ flex: '1 1 100%' }}
                color="inherit"
                variant="subtitle1"
                component="div"
              >
                Race Details
              </Typography>
            </Toolbar>
            <TableContainer component={Paper}>
              <Table size="small" aria-label="a dense table">
                <TableBody>
                  <TableRow
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell component="th" scope="row">
                      Track
                    </TableCell>
                    <TableCell align="right">
                      {bet.race.track_code.toUpperCase()}
                    </TableCell>
                  </TableRow>
                  <TableRow
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell component="th" scope="row">
                      Race Number
                    </TableCell>
                    <TableCell align="right">{bet.race.race_number}</TableCell>
                  </TableRow>
                  <TableRow
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell component="th" scope="row">
                      Race Date
                    </TableCell>
                    <TableCell align="right">{bet.race.race_date}</TableCell>
                  </TableRow>
                  <TableRow
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell component="th" scope="row">
                      Time to Post
                    </TableCell>
                    <TableCell align="right">
                      <CountdownTimer
                        timeMillis={getEffectiveTS(bet)}
                        endText="OFF"
                      />
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
        <Grid item xl={6} md={12}>
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
                Bet Details
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
    </>
  );
}
