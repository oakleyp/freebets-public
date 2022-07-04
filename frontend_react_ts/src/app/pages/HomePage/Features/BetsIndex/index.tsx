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

import { styled } from '@mui/material/styles';
import Grid from '@mui/material/Grid';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Avatar from '@mui/material/Avatar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import FolderIcon from '@mui/icons-material/Folder';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';

import { useBetIndexSlice } from './slice';
import { MultiBet, SingleBet } from 'types/Bet';
import { Folder, FolderCopy } from '@mui/icons-material';
import { Chip, Stack } from '@mui/material';

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
    <Box>
      <CircularProgress />
    </Box>
  );

  function getBetIcon(bet: any): any {
    if (bet.sub_bets) {
      return <FolderCopy />;
    }

    return <Folder />;
  }

  function getBetName(bet: any): any {
    if (bet.sub_bets) {
      const uniqTrackCodes = [
        ...new Set(bet.sub_bets.map(bet => bet.race.track_code.toUpperCase())),
      ].join(' | ');

      return `(MULTI) ${uniqTrackCodes}`;
    }

    return bet.race.track_code.toUpperCase();
  }

  function listBets(bets: any) {
    return (
      <List>
        {[...bets.multiBets, ...bets.singleBets].map(bet => (
          <ListItem>
            <ListItemAvatar>
              <Avatar>{getBetIcon(bet)}</Avatar>
            </ListItemAvatar>
            <ListItemText
              primary={getBetName(bet)}
              secondary={
                <Stack direction="row" spacing={1}>
                  <Chip label={`Min Reward = ${bet.min_reward}`} />
                  <Chip label={`Avg Reward = ${bet.avg_reward}`} />
                  <Chip label={`Max Reward = ${bet.max_reward}`} />
                </Stack>
              }
            />
          </ListItem>
        ))}
      </List>
    );
  }

  function betTable(bets: any) {
    return (
      <>
        <ListHeader sx={{ mt: 4, mb: 2 }} variant="h6">
          Upcoming Plays
        </ListHeader>
        <ListContainer>{loading ? Loader : listBets(bets)}</ListContainer>
      </>
    );
  }

  return betTable(bets);
}

const ListContainer = styled('div')(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  color: theme.palette.text.primary,
}));

const ListHeader = styled(Typography)(({ theme, ...props }) => ({
  color: theme.palette.text.primary,
}));
