/**
 *
 * MultiBetView
 *
 */
import * as React from 'react';
import { MultiBet } from 'types/Bet';
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

interface Props {
  bet: MultiBet;
}

export function MultiBetView({ bet }: Props) {
  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        {bet.sub_bets.map(bet => (
          <SingleBetView dense key={`betview-${bet.id}`} bet={bet} />
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
  );
}
