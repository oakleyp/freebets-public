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
  width: number;
  open: boolean;
  setOpen: Function;
  containerRef: MutableRefObject<Element | null>;
  filterStates: any;
  saveFilters: Function;
  resetFilters: Function;
  filterStateDirty: boolean;
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
      valueDecorator: val => val,
    },
    betStrategies: {
      label: 'Bet Strategy Types',
      openState: useState(false),
      filterState: filterStates.betStrategies.state[0],
      setFilterState: filterStates.betStrategies.state[1],
      availableFilterValues: filterStates.betStrategies.available,
      valueDecorator: val => val,
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
                  <ListItemButton sx={{ pl: 4 }}>
                    <Stack direction="column" spacing={1}>
                      {[...filterTypes[filterType].availableFilterValues]
                        .sort((a, b) => a.localeCompare(b))
                        .map(value => (
                          <FormGroup key={`${filterType}-${value}-checked`}>
                            <FormControlLabel
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
                  </ListItemButton>
                </List>
              </Collapse>
            </React.Fragment>
          ))}
        </List>
      </Drawer>
    </Box>
  );
}
