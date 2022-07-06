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

interface Props {
  bet: SingleBet;
}

export function SingleBetView({ bet }: Props) {
  return (
    <>
      <Grid container spacing={2}>
        <Grid item xs={6}>
          <Paper sx={{ height: '100%' }}>
            <Toolbar
              sx={{
                pl: { sm: 2 },
                pr: { xs: 1, sm: 1 },
                ...{
                  bgcolor: theme => theme.palette.secondary.dark,
                  color: theme => theme.palette.secondary.contrastText,
                },
              }}
            >
              <Typography
                sx={{ flex: '1 1 100%', padding: '0.5em' }}
                variant="subtitle1"
                id="tableTitle"
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
                      Betting Status
                    </TableCell>
                    <TableCell align="right">{bet.race.status}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
        <Grid item xs={6}>
          <Paper sx={{ height: '100%' }}>
            <Toolbar
              sx={{
                pl: { sm: 2 },
                pr: { xs: 1, sm: 1 },
                bgcolor: theme => theme.palette.secondary.dark,
                color: theme => theme.palette.secondary.contrastText,
              }}
            >
              <Typography
                sx={{ flex: '1 1 100%', padding: '0.5em' }}
                variant="subtitle1"
                id="tableTitle"
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
      <Box sx={{ marginTop: '2em' }}>
        <EntriesTable rows={bet.active_entries} title="Active Entries" />
      </Box>
    </>
  );
}
