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
import Tooltip from '@mui/material/Tooltip';
import { EntriesTable } from 'app/components/EntriesTable';
import { CountdownTimer } from '../CountdownTimer';
import { getEffectiveTS } from 'utils/bets';
import { BetDiffDescriptor } from 'app/pages/BetViewPage/Features/BetView/slice/types';

interface Props {
  bet: SingleBet;
  nextRefreshTs: number;
  dense?: boolean | null;
  betDiff: BetDiffDescriptor;
}

function createDiffView(
  bet: SingleBet,
  betDiff: BetDiffDescriptor,
  diffField: keyof BetDiffDescriptor,
) {
  const bddMap = {
    avgRewardDiff: 'avg_reward',
    minRewardDiff: 'min_reward',
    maxRewardDiff: 'max_reward',
  };

  const ogval = bet[bddMap[diffField]];
  const diff = betDiff[diffField];

  if (diff === 0) {
    return `$${ogval.toFixed(2)}`;
  }

  const color = diff > 0 ? 'success' : 'error';
  const changeText = diff > 0 ? 'Increased' : 'Decreased';

  return (
    <Tooltip title={`${changeText} from: ${bet[bddMap[diffField]].toFixed(2)}`}>
      <Typography color={color}>${`${(ogval + diff).toFixed(2)}`}</Typography>
    </Tooltip>
  );
}

export function SingleBetView({
  bet,
  nextRefreshTs,
  betDiff,
  dense = false,
}: Props) {
  return (
    <>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <EntriesTable
            defaultDense={dense}
            rows={bet.active_entries}
            title="Active Entries"
          />
        </Grid>
        <Grid item xs={12}>
          <EntriesTable
            defaultDense={dense}
            defaultExpanded={false}
            rows={bet.inactive_entries}
            title="Inactive Entries"
          />
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
                  <TableRow
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell component="th" scope="row">
                      Win Pool
                    </TableCell>
                    <TableCell align="right">
                      ${bet.race.win_pool_total.toFixed(2)}
                    </TableCell>
                  </TableRow>
                  <TableRow
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell component="th" scope="row">
                      Place Pool
                    </TableCell>
                    <TableCell align="right">
                      ${bet.race.place_pool_total.toFixed(2)}
                    </TableCell>
                  </TableRow>
                  <TableRow
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell component="th" scope="row">
                      Show Pool
                    </TableCell>
                    <TableCell align="right">
                      ${bet.race.show_pool_total.toFixed(2)}
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
                      {createDiffView(bet, betDiff, 'minRewardDiff')}
                    </TableCell>
                  </TableRow>
                  <TableRow
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell component="th" scope="row">
                      Avg. Reward
                    </TableCell>
                    <TableCell align="right">
                      {createDiffView(bet, betDiff, 'avgRewardDiff')}
                    </TableCell>
                  </TableRow>
                  <TableRow
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell component="th" scope="row">
                      Max Reward
                    </TableCell>
                    <TableCell align="right">
                      {createDiffView(bet, betDiff, 'maxRewardDiff')}
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
