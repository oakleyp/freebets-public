import { styled, useTheme } from '@mui/material/styles';
import Drawer from '@mui/material/Drawer';
import IconButton from '@mui/material/IconButton';
import List from '@mui/material/List';
import ListSubheader from '@mui/material/ListSubheader';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckIcon from '@mui/icons-material/Check';
import Collapse from '@mui/material/Collapse';
import ExpandMore from '@mui/icons-material/ExpandMore';
import ExpandLess from '@mui/icons-material/ExpandLess';
import Box from '@mui/material/Box';
import React, { MutableRefObject, useState } from 'react';
import Divider from '@mui/material/Divider';
import Switch from '@mui/material/Switch';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Stack from '@mui/material/Stack';
import Tooltip from '@mui/material/Tooltip';

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),
  // necessary for content to be below app bar
  ...theme.mixins.toolbar,
  justifyContent: 'flex-end',
}));

interface FilterDrawerProps {
  width: string;
  open: boolean;
  setOpen: Function;
  containerRef: MutableRefObject<Element | null>;
  filterStates: any;
  saveFilters: Function;
  resetFilters: Function;
  filterStateDirty: boolean;
}

const betStratTypeDisplayMap = {
  AI_ALL_WIN_ARB: '(AI) All Win',
  AI_BOX_WIN_ARB: '(AI) Box Win',
  AI_WIN_BET: '(AI) Win',
  BOOK_ALL_WIN_ARB: '(Book) All Win',
  BOOK_BOX_WIN_ARB: '(Book) Box Win',
  BOOK_WIN_BET: '(Book) Win',
};

const betTypeDisplayMap = {
  ALL_WIN_ARB: 'All Win',
  BOX_WIN_ARB: 'Box Win',
  WIN_BET: 'Win',
};

function getBetStratTypeDisplay(val: string): string {
  return betStratTypeDisplayMap[val] || val;
}

function getBetTypeDisplay(val: string): string {
  return betTypeDisplayMap[val] || val;
}

export function FilterDrawer({
  containerRef,
  width,
  open,
  setOpen,
  filterStates,
  saveFilters,
  resetFilters,
  filterStateDirty,
}: FilterDrawerProps) {
  const theme = useTheme();

  const filterTypes = {
    betTypes: {
      label: 'Bet Types',
      openState: useState(false),
      filterState: filterStates.betTypes.state[0],
      setFilterState: filterStates.betTypes.state[1],
      availableFilterValues: filterStates.betTypes.available,
      valueDecorator: val => getBetTypeDisplay(val.replace('BetType.', '')),
    },
    betStrategies: {
      label: 'Bet Strategy Types',
      openState: useState(false),
      filterState: filterStates.betStrategies.state[0],
      setFilterState: filterStates.betStrategies.state[1],
      availableFilterValues: filterStates.betStrategies.available,
      valueDecorator: val =>
        getBetStratTypeDisplay(val.replace('BetStrategyType.', '')),
    },
    trackCodes: {
      label: 'Tracks',
      openState: useState(false),
      filterState: filterStates.trackCodes.state[0],
      setFilterState: filterStates.trackCodes.state[1],
      availableFilterValues: filterStates.trackCodes.available,
      valueDecorator: val => val.toUpperCase(),
    },
  };

  // console.log(filterTypes);

  function handleFilterSwitch(
    filterType: string,
    value: string,
    e: React.ChangeEvent<HTMLInputElement>,
  ) {
    const newState = e.target.checked
      ? [...filterTypes[filterType].filterState, value]
      : [...filterTypes[filterType].filterState.filter(v => v !== value)];

    filterTypes[filterType].setFilterState(newState);
  }

  function handleFilterMenuItemClick(filterType) {
    const [open, setOpen] = filterTypes[filterType].openState;
    setOpen(!open);
  }

  return (
    <Box
      component="nav"
      sx={{ width: { sm: width }, flexShrink: { sm: 0 } }}
      aria-label="mailbox folders"
    >
      <Drawer
        sx={{
          width: width,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: width,
            boxSizing: 'border-box',
            position: 'absolute',
          },
        }}
        container={containerRef.current}
        variant="persistent"
        anchor="left"
        open={open}
      >
        <DrawerHeader>
          <IconButton onClick={() => setOpen(false)}>
            {theme.direction === 'ltr' ? (
              <ChevronLeftIcon />
            ) : (
              <ChevronRightIcon />
            )}
          </IconButton>
        </DrawerHeader>
        <Divider />
        <List
          subheader={
            <ListSubheader component="div">
              <Stack direction="row">
                <span style={{ flex: '1' }}>Filters</span>
                <Tooltip title={'Revert filter changes'}>
                  <IconButton
                    size="small"
                    disabled={!filterStateDirty}
                    onClick={() => resetFilters()}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title={'Update search'}>
                  <IconButton
                    color="success"
                    size="small"
                    disabled={!filterStateDirty}
                    onClick={() => saveFilters()}
                  >
                    <CheckIcon />
                  </IconButton>
                </Tooltip>
              </Stack>
            </ListSubheader>
          }
        >
          {Object.keys(filterTypes).map(filterType => (
            <React.Fragment key={`${filterType}-menu`}>
              <ListItem disablePadding>
                <ListItemButton
                  onClick={() => handleFilterMenuItemClick(filterType)}
                >
                  <ListItemText primary={filterTypes[filterType].label} />
                  {filterTypes[filterType].openState[0] ? (
                    <ExpandLess />
                  ) : (
                    <ExpandMore />
                  )}
                </ListItemButton>
              </ListItem>
              <Collapse
                in={filterTypes[filterType].openState[0]}
                timeout="auto"
                unmountOnExit
              >
                <List component="div" disablePadding>
                  <ListItemText sx={{ pl: 4 }}>
                    <Stack
                      direction="column"
                      spacing={1}
                      sx={{ maxWidth: '100%' }}
                    >
                      {[...filterTypes[filterType].availableFilterValues]
                        .sort((a, b) =>
                          filterTypes[filterType]
                            .valueDecorator(a)
                            .localeCompare(
                              filterTypes[filterType].valueDecorator(b),
                            ),
                        )
                        .map(value => (
                          <FormGroup key={`${filterType}-${value}-checked`}>
                            <FormControlLabel
                              sx={{ maxWidth: '100%', wordBreak: 'break-word' }}
                              control={
                                <Switch
                                  checked={filterTypes[
                                    filterType
                                  ].filterState.includes(value)}
                                  onChange={e =>
                                    handleFilterSwitch(filterType, value, e)
                                  }
                                />
                              }
                              label={filterTypes[filterType].valueDecorator(
                                value,
                              )}
                            />
                          </FormGroup>
                        ))}
                    </Stack>
                  </ListItemText>
                </List>
              </Collapse>
            </React.Fragment>
          ))}
        </List>
      </Drawer>
    </Box>
  );
}
