import React, { useState, memo, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useSelector, useDispatch } from 'react-redux';
import {
  selectBets,
  selectError,
  selectLoading,
  selectCurrentBetSearchParams,
  selectSelectedBet,
} from './slice/selectors';

import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';

import { useBetIndexSlice } from './slice';
import { MultiBet, SingleBet } from 'types/Bet';

export function BetIndex() {
  const { actions } = useBetIndexSlice();

  const bets = useSelector(selectBets);
  const loading = useSelector(selectLoading);
  const error = useSelector(selectError);
  const currentBetSearchParams = useSelector(selectCurrentBetSearchParams);

  const dispatch = useDispatch();

  const useEffectOnMount = (effect: React.EffectCallback) => {
    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(effect, []);
  };

  useEffectOnMount(() => {
    console.log('loading');
    dispatch(actions.loadBets());
  });

  const [activeIndex, setActiveIndex] = useState(-1);
  const [menuVisible, setMenuVisible] = useState(false);

  // Local state to hold uncommitted filter changes
  const [betTypes, setBetTypes] = useState(
    currentBetSearchParams.betTypes || [],
  );
  const [betStrategies, setBetStrategies] = useState(
    currentBetSearchParams.betStratTypes || [],
  );
  const [trackCodes, setTrackCodes] = useState(
    currentBetSearchParams.trackCodes || [],
  );

  useEffect(() => {
    setBetTypes(currentBetSearchParams.betTypes || []);
    setBetStrategies(currentBetSearchParams.betStratTypes || []);
    setTrackCodes(currentBetSearchParams.trackCodes || []);
  }, [currentBetSearchParams]);

  // const handleTabClick = (evt: React.FormEvent<HTMLFormElement>, titleProps) => {
  //   const { index } = titleProps;
  //   const newIndex = activeIndex === index ? -1 : index;

  //   setActiveIndex(newIndex);
  // };

  // const handleFilterSaveClick = () => {
  //   dispatch(actions.setBetSearchParams({
  //     ...currentBetSearchParams,
  //     betTypes,
  //     betStratTypes: betStrategies,
  //     trackCodes: trackCodes,
  //   }));
  // };

  const panes = [
    {
      menuItem: "Today's Bets",
      render: () => null,
    },
    {
      menuItem: 'Upcoming',
      render: () => null,
    },
  ];

  const Loader = (
    <Box sx={{ display: 'flex' }}>
      <CircularProgress />
    </Box>
  );

  function getBetName(bet: any): any {
    if (bet.sub_bets) {
      const uniqTrackCodes = [
        ...new Set(bet.sub_bets.map(bet => bet.race.track_code.toUpperCase())),
      ].join(' | ');

      return `(MULTI) ${uniqTrackCodes}`;
    }

    return bet.race.track_code.toUpperCase();
  }

  function betTable(bets: any) {
    return (
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>Bet</TableCell>
              <TableCell align="right">Cost</TableCell>
              <TableCell align="right">Min Reward</TableCell>
              <TableCell align="right">Avg Reward</TableCell>
              <TableCell align="right">Max Reward</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {[...bets.singleBets, ...bets.multiBets].map((bet: any) => (
              <TableRow
                key={bet.title}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell component="th" scope="row">
                  {getBetName(bet)}
                </TableCell>
                <TableCell align="right">{bet.cost}</TableCell>
                <TableCell align="right">{bet.min_reward}</TableCell>
                <TableCell align="right">{bet.avg_reward}</TableCell>
                <TableCell align="right">{bet.max_reward}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  }

  return <>{loading ? Loader : betTable(bets)}</>;
}
