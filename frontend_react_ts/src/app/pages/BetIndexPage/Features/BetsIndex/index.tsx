import React, {
  useState,
  useEffect,
  useRef,
  MutableRefObject,
  createRef,
  useMemo,
  useCallback,
} from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  selectBets,
  selectError,
  selectLoading,
  selectCurrentBetSearchParams,
  selectAvailableFilterValues,
  selectNextRefreshTs,
  selectCountdownRefreshEnabled,
} from './slice/selectors';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';

import { styled } from '@mui/material/styles';
import List from '@mui/material/List';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import MuiAppBar, { AppBarProps as MuiAppBarProps } from '@mui/material/AppBar';
import MenuIcon from '@mui/icons-material/Menu';
import RefreshIcon from '@mui/icons-material/Refresh';
import PauseIcon from '@mui/icons-material/Pause';
import ResumeIcon from '@mui/icons-material/PlayArrow';
import Box from '@mui/material/Box';
import Skeleton from '@mui/material/Skeleton';
import Stack from '@mui/material/Stack';
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
import { CountdownTimer } from 'app/components/CountdownTimer';
import { TimeseriesChart } from './components/TimeseriesChart';

dayjs.extend(utc);

export function BetIndex() {
  const { actions } = useBetIndexSlice();

  const bets = useSelector(selectBets);
  const loading = useSelector(selectLoading);
  const error = useSelector(selectError);
  const currentBetSearchParams = useSelector(selectCurrentBetSearchParams);
  const availableFilterValues = useSelector(selectAvailableFilterValues);
  const nextRefreshTs = useSelector(selectNextRefreshTs);
  const countdownRefreshEnabled = useSelector(selectCountdownRefreshEnabled);

  const now = dayjs().utc();
  const nowMillis = now.unix() * 1000;
  const hasRefreshExpired = nextRefreshTs && nextRefreshTs > nowMillis;
  const effectiveNextRefreshTs = hasRefreshExpired
    ? nextRefreshTs
    : now.add(10, 'minute').unix() * 1000;

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

  const allBets = useMemo(
    () => [...bets.multiBets, ...bets.singleBets],
    [bets],
  );

  const betItemRefMap = useRef({});

  useEffect(() => {
    const newmap = allBets.reduce(
      (map, bet) => ({
        ...map,
        [bet.id]: betItemRefMap.current[bet.id],
      }),
      {},
    );

    betItemRefMap.current = newmap;
  }, [allBets]);

  function listBets(bets: any) {
    return (
      <List>
        {[...allBets]
          .sort((a, b) => getEffectiveTS(a) - getEffectiveTS(b))
          .map(bet => (
            <div
              ref={el => (betItemRefMap.current[bet.id] = el)}
              key={`betitem-${bet.id}`}
            >
              <BetListItem bet={bet} />
            </div>
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

  const handleBetSelection = useCallback(bet => {
    betItemRefMap.current[bet.id].scrollIntoView({
      behavior: 'smooth',
    });
  }, []);

  const drawerContainerRef: MutableRefObject<Element | null> = useRef(null);

  function betTable(bets: any) {
    return (
      <>
        <Box sx={{ margin: '1em 0' }}>
          {!loading && bets.singleBets.length && (
            <TimeseriesChart bets={allBets} onSelection={handleBetSelection} />
          )}
          {loading && (
            <>
              <Skeleton
                variant="rectangular"
                width={'100%'}
                height={20}
                sx={{ marginBottom: '0.5em' }}
              />
              <Skeleton
                variant="rectangular"
                animation="wave"
                width={'100%'}
                height={100}
              />
            </>
          )}
        </Box>
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
            <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
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
              <Typography variant="h6" noWrap component="div" sx={{ flex: 1 }}>
                Upcoming Plays
              </Typography>
              {!error && (
                <Stack direction="row" spacing={0} sx={{ flex: 0 }}>
                  <IconButton
                    color="inherit"
                    edge="end"
                    sx={{ mr: 0 }}
                    disabled={loading}
                    onClick={() => dispatch(actions.loadBets())}
                    size="small"
                  >
                    <RefreshIcon />
                  </IconButton>
                  <IconButton
                    color="inherit"
                    edge="end"
                    sx={{ mr: 0 }}
                    disabled={loading}
                    onClick={() =>
                      dispatch(
                        actions.setCountdownRefreshEnabled(
                          !countdownRefreshEnabled,
                        ),
                      )
                    }
                    size="small"
                  >
                    {countdownRefreshEnabled || loading ? (
                      <PauseIcon />
                    ) : (
                      <ResumeIcon />
                    )}
                  </IconButton>
                  <IconButton
                    color="inherit"
                    edge="end"
                    sx={{ mr: 0 }}
                    disabled={loading || !countdownRefreshEnabled}
                    onClick={() => dispatch(actions.loadBets())}
                    size="small"
                  >
                    {loading ? (
                      <Skeleton width={80} />
                    ) : (
                      <CountdownTimer
                        timeMillis={effectiveNextRefreshTs}
                        onEnd={() =>
                          !loading &&
                          countdownRefreshEnabled &&
                          dispatch(actions.loadBets())
                        }
                        endText="Refreshing..."
                        running={!loading && countdownRefreshEnabled}
                      />
                    )}
                  </IconButton>
                </Stack>
              )}
              {error && (
                <IconButton
                  color="inherit"
                  edge="end"
                  sx={{ mr: 1, flex: 0 }}
                  disabled={loading}
                  onClick={() => dispatch(actions.loadBets())}
                  size="small"
                >
                  <RefreshIcon />
                </IconButton>
              )}
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
      </>
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

const drawerWidth = window.screen.width >= 1024 ? '18vw' : '80vw';

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
