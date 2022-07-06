import React, { useState, useEffect, useRef, MutableRefObject } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  selectBets,
  selectError,
  selectLoading,
  selectCurrentBetSearchParams,
  selectAvailableFilterValues,
} from './slice/selectors';

import { styled } from '@mui/material/styles';
import List from '@mui/material/List';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import MuiAppBar, { AppBarProps as MuiAppBarProps } from '@mui/material/AppBar';
import MenuIcon from '@mui/icons-material/Menu';
import Box from '@mui/material/Box';
import headerImage from '../../assets/wow.gif';
import LinearProgress, {
  linearProgressClasses,
} from '@mui/material/LinearProgress';
import { FilterDrawer } from './components/FilterDrawer';
import { useBetIndexSlice } from './slice';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import Paper from '@mui/material/Paper';
import Toolbar from '@mui/material/Toolbar';
import { BetsErrorType } from './slice/types';
import { BetListItem } from './components/BetListItem';
import { getEffectiveTS } from 'utils/bets';

export function BetIndex() {
  const { actions } = useBetIndexSlice();

  const bets = useSelector(selectBets);
  const loading = useSelector(selectLoading);
  const error = useSelector(selectError);
  const currentBetSearchParams = useSelector(selectCurrentBetSearchParams);
  const availableFilterValues = useSelector(selectAvailableFilterValues);

  const dispatch = useDispatch();

  const useEffectOnMount = (effect: React.EffectCallback) => {
    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(effect, []);
  };

  useEffectOnMount(() => {
    dispatch(actions.loadBets());
  });

  const [filterOpen, setFilterOpen] = useState(false);
  const [filterStateDirty, setFilterStateDirty] = useState(false);

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

  // Wrapper for funcs where calling should signify a "dirty" filter state;
  // Potentially, this could be better solved by moving all state to redux and using
  // its immutability advantages to do a quick compare of new/old state, rather than manually tracking.
  function stateMutWrapper(func) {
    return function (...args) {
      setFilterStateDirty(true);
      return func(...args);
    };
  }

  useEffect(() => {
    setBetTypes(currentBetSearchParams.betTypes || []);
    setBetStrategies(currentBetSearchParams.betStratTypes || []);
    setTrackCodes(currentBetSearchParams.trackCodes || []);
  }, [currentBetSearchParams]);

  const handleFilterSaveClick = () => {
    dispatch(
      actions.setBetSearchParams({
        ...currentBetSearchParams,
        betTypes,
        betStratTypes: betStrategies,
        trackCodes: trackCodes,
      }),
    );
    setFilterStateDirty(false);
  };

  const handleFilterResetClick = () => {
    setBetTypes(currentBetSearchParams.betTypes || []);
    setBetStrategies(currentBetSearchParams.betStratTypes || []);
    setTrackCodes(currentBetSearchParams.trackCodes || []);
    setFilterStateDirty(false);
  };

  const Loader = (
    <Box sx={{}}>
      <img src={headerImage} alt="" style={{ width: '100%' }} />
      <BorderLinearProgress />
    </Box>
  );

  function listBets(bets: any) {
    return (
      <List>
        {[...bets.multiBets, ...bets.singleBets]
          .sort((a, b) => getEffectiveTS(b) - getEffectiveTS(a))
          .map(bet => (
            <BetListItem bet={bet} key={`betitem-${bet.id}`} />
          ))}
      </List>
    );
  }

  function loadErrorOr(fn: Function) {
    if (loading) {
      return Loader;
    }

    if (error) {
      if (error === BetsErrorType.NO_BETS_ERROR) {
        return (
          <Alert severity="info">
            <AlertTitle>No bets to display</AlertTitle>
            The current search returned no bets.
          </Alert>
        );
      }

      return (
        <Alert severity="error">
          <AlertTitle>Something went wrong...</AlertTitle>
          Unable to load bets — <strong>{`${error}`}</strong>
        </Alert>
      );
    }

    return fn();
  }

  const drawerContainerRef: MutableRefObject<Element | null> = useRef(null);

  function betTable(bets: any) {
    return (
      <Box
        component={Paper}
        ref={drawerContainerRef}
        id="drawcontainer"
        sx={{ position: 'relative' }}
      >
        <AppBar
          open={filterOpen}
          sx={{
            position: 'static',
          }}
        >
          <Toolbar sx={{ display: 'flex' }}>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              onClick={() => {
                setFilterOpen(true);
              }}
              edge="start"
              sx={{ mr: 2, ...(filterOpen && { display: 'none' }) }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div">
              Upcoming Plays
            </Typography>
          </Toolbar>
        </AppBar>
        <FilterDrawer
          containerRef={drawerContainerRef}
          width={drawerWidth}
          open={filterOpen}
          setOpen={setFilterOpen}
          filterStates={{
            betTypes: {
              state: [betTypes, stateMutWrapper(setBetTypes)],
              available: availableFilterValues.betTypes,
            },
            betStrategies: {
              state: [betStrategies, stateMutWrapper(setBetStrategies)],
              available: availableFilterValues.betStratTypes,
            },
            trackCodes: {
              state: [trackCodes, stateMutWrapper(setTrackCodes)],
              available: availableFilterValues.trackCodes,
            },
          }}
          saveFilters={handleFilterSaveClick}
          resetFilters={handleFilterResetClick}
          filterStateDirty={filterStateDirty}
        />
        <Main open={filterOpen}>
          <ListContainer>{loadErrorOr(() => listBets(bets))}</ListContainer>
        </Main>
      </Box>
    );
  }

  return betTable(bets);
}

const ListContainer = styled('div')(({ theme }) => ({
  backgroundColor: 'transparent',
  color: theme.palette.text.primary,
  overflowY: 'auto',
  maxHeight: '60vh',
  marginLeft: `${drawerWidth}`,
  padding: '0 0.2em',
}));

const ListHeader = styled(Typography)(({ theme, ...props }) => ({
  color: theme.palette.text.primary,
}));

const drawerWidth = '10vw';

const Main = styled('main', { shouldForwardProp: prop => prop !== 'open' })<{
  open?: boolean;
}>(({ theme, open }) => ({
  flexGrow: 1,
  padding: theme.spacing(1),
  transition: theme.transitions.create('margin', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  marginLeft: `-${drawerWidth}`,
  ...(open && {
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
    marginLeft: 0,
  }),
}));

interface AppBarProps extends MuiAppBarProps {
  open?: boolean;
}

const AppBar = styled(MuiAppBar, {
  shouldForwardProp: prop => prop !== 'open',
})<AppBarProps>(({ theme, open }) => ({
  transition: theme.transitions.create(['margin', 'width'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  ...(open && {
    width: `calc(100% - ${drawerWidth})`,
    marginLeft: `${drawerWidth}`,
    transition: theme.transitions.create(['margin', 'width'], {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const BorderLinearProgress = styled(LinearProgress)(({ theme }) => ({
  height: 6,
  borderRadius: 5,
  [`&.${linearProgressClasses.colorPrimary}`]: {
    backgroundColor:
      theme.palette.grey[theme.palette.mode === 'light' ? 200 : 800],
  },
  [`& .${linearProgressClasses.bar}`]: {
    borderRadius: 5,
    backgroundColor: theme.palette.mode === 'light' ? '#1a90ff' : '#308fe8',
  },
}));
