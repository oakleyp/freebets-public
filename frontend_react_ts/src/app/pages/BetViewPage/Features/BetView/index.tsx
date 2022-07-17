import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  selectBet,
  selectBetId,
  selectBetMetaType,
  selectError,
  selectLoading,
  selectNextRefreshTs,
  selectBetDiff,
} from './slice/selectors';

import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';

import { useBetViewSlice } from './slice';
import { Alert, AlertTitle, Link } from '@mui/material';
import { SingleBetView } from 'app/components/SingleBetView';
import { MultiBetView } from 'app/components/MultiBetView';
import { BetDiff } from './components/BetDiff';
import { MultiBet, SingleBet } from 'types/Bet';
import { BetViewErrorType } from './slice/types';

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
  const nextRefreshTs = useSelector(selectNextRefreshTs);
  const betDiff = useSelector(selectBetDiff);

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
    <Box sx={{ display: 'flex', justifyContent: 'center', width: '100%' }}>
      <CircularProgress />
    </Box>
  );

  function getErrorMessage(error: BetViewErrorType): React.ReactNode {
    if (error === BetViewErrorType.NOT_FOUND_ERROR) {
      return (
        <span>
          This bet has expired. Go <Link href="/">home</Link> to get a fresh
          one.
        </span>
      );
    }

    return (
      <span>
        Unable to load bet {betId} — <strong>{`${error}`}</strong>
      </span>
    );
  }

  if (error) {
    content = (
      <Alert severity="error">
        <AlertTitle>Something went wrong...</AlertTitle>
        {getErrorMessage(error)}
      </Alert>
    );
  } else if (!loading && bet && betDiff) {
    content =
      betMetaType === 'single' ? (
        <>
          <BetDiff betDiff={betDiff} />
          <br />
          <SingleBetView
            bet={bet as SingleBet}
            nextRefreshTs={Number(nextRefreshTs)}
            betDiff={betDiff}
          />
        </>
      ) : (
        <>
          <BetDiff betDiff={betDiff} />
          <br />
          <MultiBetView
            bet={bet as MultiBet}
            nextRefreshTs={Number(nextRefreshTs)}
            betDiff={betDiff}
          />
        </>
      );
  }

  return content;
}
