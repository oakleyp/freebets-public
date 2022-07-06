import React, {
  useState,
  memo,
  useEffect,
  useRef,
  MutableRefObject,
} from 'react';
import PropTypes from 'prop-types';
import { useSelector, useDispatch } from 'react-redux';
import {
  selectBets,
  selectError,
  selectLoading,
  selectCurrentBetSearchParams,
  selectSelectedBet,
  selectAvailableFilterValues,
} from './slice/selectors';

import { styled, useTheme } from '@mui/material/styles';
import Collapse from '@mui/material/Collapse';
import Grid from '@mui/material/Grid';
import List from '@mui/material/List';
import ListSubheader from '@mui/material/ListSubheader';
import Drawer from '@mui/material/Drawer';
import ListItem from '@mui/material/ListItem';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Avatar from '@mui/material/Avatar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import FolderIcon from '@mui/icons-material/Folder';
import CircularProgress from '@mui/material/CircularProgress';
import MuiAppBar, { AppBarProps as MuiAppBarProps } from '@mui/material/AppBar';
import Divider from '@mui/material/Divider';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import MailIcon from '@mui/icons-material/Mail';
import Tooltip from '@mui/material/Tooltip';
import Box from '@mui/material/Box';
import headerImage from '../../assets/wow.gif';
import LinearProgress, {
  linearProgressClasses,
} from '@mui/material/LinearProgress';
import Link, { LinkProps } from '@mui/material/Link';
import { FilterDrawer } from './components/FilterDrawer';
import { useBetIndexSlice } from './slice';
import { MultiBet, SingleBet } from 'types/Bet';
import { AirplaneTicket, FileCopy } from '@mui/icons-material';
import {
  Alert,
  AlertTitle,
  Chip,
  ListItemButton,
  Paper,
  Stack,
  Toolbar,
} from '@mui/material';

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

  // Wrapper for funcs where calling should signal a "dirty" filter state
  // Potentially, this could be better solved by moving all state to redux and using
  // its immutability advantages to do a quick compare of new/old state, rather than manually tracking
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
          <Tooltip title="Open play in new tab">
            <BetListItem
              component={Link}
              href={`/bets/${bet.id}`}
              target="_blank"
            >
              <ListItemAvatar>
                <Avatar>{getBetIcon(bet)}</Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={getBetName(bet)}
                secondary={
                  <>
                    <Stack direction="row" spacing={1}>
                      <span>{`Cost = $${bet.cost.toFixed(2)}`}</span>
                      <span>{`Min Reward = $${bet.min_reward.toFixed(
                        2,
                      )}`}</span>
                      <span>{`Avg Reward = $${bet.avg_reward.toFixed(
                        2,
                      )}`}</span>
                      <span>{`Max Reward = $${bet.max_reward.toFixed(
                        2,
                      )}`}</span>
                    </Stack>
                    {getTags(bet)}
                  </>
                }
              />
            </BetListItem>
          </Tooltip>
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
  marginLeft: `${drawerWidth}px`,
  padding: '0 0.2em',
}));

const BetListItem = styled(ListItemButton)<
  LinkProps & { component?: React.ElementType }
>(({ theme, ...props }) => ({
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

const drawerWidth = 240;

const Main = styled('main', { shouldForwardProp: prop => prop !== 'open' })<{
  open?: boolean;
}>(({ theme, open }) => ({
  flexGrow: 1,
  padding: theme.spacing(1),
  transition: theme.transitions.create('margin', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  marginLeft: `-${drawerWidth}px`,
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
    width: `calc(100% - ${drawerWidth}px)`,
    marginLeft: `${drawerWidth}px`,
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
