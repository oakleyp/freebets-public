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
import {
  AirplaneTicket,
  FileCopy,
  Folder,
  FolderCopy,
  InsertDriveFile,
} from '@mui/icons-material';
import {
  Alert,
  AlertTitle,
  Chip,
  ListItemButton,
  Paper,
  Stack,
} from '@mui/material';
import { JsxChild, JsxElement, JsxExpression } from 'typescript';

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
    <Box sx={{ display: 'flex', justifyContent: 'center', padding: '2em' }}>
      <CircularProgress />
    </Box>
  );

  function getBetIcon(bet: any): any {
    if (bet.sub_bets) {
      return <FileCopy />;
    }

    return <AirplaneTicket />;
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

  const tagColorMap = {
    'good value': 'primary',
    free: 'warning',
  };

  function tagColor(tagName: string) {
    return tagColorMap[tagName];
  }

  function getTags(bet: any): any {
    return (
      <TagsContainer>
        <Stack direction="row" spacing={1}>
          {bet.tags.map(tag => (
            <Chip label={tag.name} color={tagColor(tag.name.toLowerCase())} />
          ))}
        </Stack>
      </TagsContainer>
    );
  }

  function listBets(bets: any) {
    return (
      <List>
        {[...bets.multiBets, ...bets.singleBets].map(bet => (
          <BetListItem>
            <ListItemAvatar>
              <Avatar>{getBetIcon(bet)}</Avatar>
            </ListItemAvatar>
            <ListItemText
              primary={getBetName(bet)}
              secondary={
                <>
                  <Stack direction="row" spacing={1}>
                    <span>{`Cost = ${bet.cost.toFixed(2)}`}</span>
                    <span>{`Min Reward = ${bet.min_reward.toFixed(2)}`}</span>
                    <span>{`Avg Reward = ${bet.avg_reward.toFixed(2)}`}</span>
                    <span>{`Max Reward = ${bet.max_reward.toFixed(2)}`}</span>
                  </Stack>
                  {getTags(bet)}
                </>
              }
            />
          </BetListItem>
        ))}
      </List>
    );
  }

  function loadErrorOr(fn: Function) {
    if (loading) {
      return Loader;
    }

    if (error) {
      return (
        <Alert severity="error">
          <AlertTitle>Something went wrong...</AlertTitle>
          Unable to load bets — <strong>{`${error}`}</strong>
        </Alert>
      );
    }

    return fn();
  }

  function betTable(bets: any) {
    return (
      <Paper>
        <ListHeader sx={{ mt: 4, mb: 2 }} variant="h6">
          Upcoming Plays
        </ListHeader>
        <ListContainer>{loadErrorOr(() => listBets(bets))}</ListContainer>
      </Paper>
    );
  }

  return betTable(bets);
}

const ListContainer = styled('div')(({ theme }) => ({
  backgroundColor: 'transparent',
  color: theme.palette.text.primary,
  overflowY: 'auto',
  maxHeight: '60vh',
}));

const BetListItem = styled(ListItemButton)(({ theme, ...props }) => ({
  paddingTop: '8px',
  paddingBottom: '16px',
  border: '1px solid',
  margin: '0.5em 0',
  borderRadius: '5px',
}));

const ListHeader = styled(Typography)(({ theme, ...props }) => ({
  color: theme.palette.text.primary,
}));

const TagsContainer = styled('div')(({ theme, ...props }) => ({
  paddingTop: '0.4em',
}));
