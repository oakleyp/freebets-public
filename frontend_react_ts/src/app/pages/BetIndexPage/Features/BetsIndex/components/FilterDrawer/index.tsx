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
}

export function FilterDrawer({
  containerRef,
  width,
  open,
  setOpen,
  filterStates,
}: FilterDrawerProps) {
  const theme = useTheme();

  const filterTypes = {
    betTypes: {
      label: 'Bet Types',
      openState: useState(false),
      filterState: filterStates.betTypes.state,
      valueDecorator: val => val,
    },
    betStrategies: {
      label: 'Bet Strategy Types',
      openState: useState(false),
      filterState: filterStates.betStrategies.state,
      valueDecorator: val => val,
    },
    trackCodes: {
      label: 'Tracks',
      openState: useState(false),
      filterState: filterStates.trackCodes.state,
      valueDecorator: val => val.toUpperCase(),
    },
  };

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
          subheader={<ListSubheader component="div">Filters</ListSubheader>}
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
                      {filterTypes[filterType].filterState[0].map(value => (
                        <FormGroup key={`${filterType}-${value}-checked`}>
                          <FormControlLabel
                            control={<Switch defaultChecked />}
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
