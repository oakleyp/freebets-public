import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  selectBet,
  selectBetId,
  selectBetMetaType,
  selectError,
  selectLoading,
} from './slice/selectors';

import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';

import { useBetViewSlice } from './slice';
import { Alert, AlertTitle } from '@mui/material';
import { SingleBetView } from 'app/components/SingleBetView';
import { MultiBetView } from 'app/components/MultiBetView';
import { MultiBet, SingleBet } from 'types/Bet';

interface Props {
  betId: string;
}

export function BetView(props: Props) {
  const { actions } = useBetViewSlice();
  const initBetId = props.betId;

  const bet = useSelector(selectBet);
  const loading = useSelector(selectLoading);
  const error = useSelector(selectError);
  const betId = useSelector(selectBetId);
  const betMetaType = useSelector(selectBetMetaType);

  const dispatch = useDispatch();

  const useEffectOnMount = (effect: React.EffectCallback) => {
    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(effect, []);
  };

  useEffectOnMount(() => {
    dispatch(actions.setBetId(initBetId));
  });

  useEffect(() => {
    if (betId) {
      dispatch(actions.loadBet());
    }
  }, [betId, actions, dispatch]);

  let content = (
    <Box>
      <CircularProgress />
    </Box>
  );

  if (error) {
    content = (
      <Alert severity="error">
        <AlertTitle>Something went wrong...</AlertTitle>
        Unable to load bet {betId} — <strong>{`${error}`}</strong>
      </Alert>
    );
  } else if (!loading && bet) {
    content =
      betMetaType === 'single' ? (
        <SingleBetView bet={bet as SingleBet} />
      ) : (
        <MultiBetView bet={bet as MultiBet} />
      );
  }

  return content;
}
