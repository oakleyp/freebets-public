import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  selectBet,
  selectBetBackground,
  selectErrorBackground,
  selectLoadingBackground,
  selectNextRefreshTs,
  selectBetMetaType,
} from '../../slice/selectors';

import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';

import { useBetViewSlice } from '../../slice';
import { Alert, AlertTitle, Link, AlertColor, IconButton } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { MultiBet, narrowBetType, SingleBet } from 'types/Bet';
import { BetDiffDescriptor, BetViewErrorType } from '../../slice/types';
import { CountdownTimer } from 'app/components/CountdownTimer';

interface BetDiffMessage {
  title: string;
  severity: AlertColor;
  body: string;
}

function getBetDiffMessages(descriptor: BetDiffDescriptor): BetDiffMessage {
  if (descriptor.avgRewardDiff === 0) {
    return {
      title: 'No recent value change.',
      severity: 'info',
      body: "This bet's value is unchanged since the last refresh.",
    };
  }

  return {
    title:
      descriptor.avgRewardDiff > 0
        ? 'Avg Payout Increase'
        : 'Avg Payout Decrease',
    severity: descriptor.avgRewardDiff > 0 ? 'success' : 'error',
    body:
      descriptor.avgRewardDiff > 0
        ? "This bet's average payout has increased since the last refresh"
        : "This bet's average payout has decreased since the last refresh.",
  };
}

interface Props {
  betDiff: BetDiffDescriptor;
}

export function BetDiff(props: Props) {
  const { actions } = useBetViewSlice();
  const { betDiff } = props;

  const bet = useSelector(selectBet);
  const betBackground = useSelector(selectBetBackground);
  const betMetaType = useSelector(selectBetMetaType);
  const loading = useSelector(selectLoadingBackground);
  const error = useSelector(selectErrorBackground);
  const nextRefreshTs = useSelector(selectNextRefreshTs);

  const dispatch = useDispatch();

  const useEffectOnMount = (effect: React.EffectCallback) => {
    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(effect, []);
  };

  if (
    !bet ||
    !betBackground ||
    !betMetaType ||
    !nextRefreshTs ||
    error === BetViewErrorType.NOT_FOUND_ERROR
  ) {
    return (
      <Alert severity="error">
        <AlertTitle>Bet Expired</AlertTitle>
        This bet was found to have no value in the latest refresh, and no longer
        exists.
      </Alert>
    );
  }

  const refreshIcon = (
    <IconButton
      color="inherit"
      edge="end"
      sx={{ mr: 0 }}
      disabled={loading}
      onClick={() => dispatch(actions.loadBetBackground())}
      size="small"
    >
      <RefreshIcon fontSize="small" />
    </IconButton>
  );

  const betDiffMessages = getBetDiffMessages(betDiff);

  return (
    <Alert severity={betDiffMessages.severity}>
      <AlertTitle>{betDiffMessages.title}</AlertTitle>
      {loading ? <CircularProgress /> : betDiffMessages.body}
      <br />
      Next Refresh:{' '}
      {!loading && !error && (
        <CountdownTimer
          timeMillis={nextRefreshTs}
          onEnd={() => dispatch(actions.loadBetBackground())}
          endText="Loading..."
        />
      )}{' '}
      {!loading && refreshIcon}
    </Alert>
  );
}
