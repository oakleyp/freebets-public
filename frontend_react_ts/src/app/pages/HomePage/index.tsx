import { AppBar } from 'app/components/AppBar/Loadable';
import { BetIndex } from './Features/BetsIndex';
import * as React from 'react';
import { Helmet } from 'react-helmet-async';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import Badge from '@mui/material/Badge';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import { Copyright } from 'app/components/Copyright';
import MenuIcon from '@mui/icons-material/Menu';
import NotificationsIcon from '@mui/icons-material/Notifications';
import { useDispatch, useSelector } from 'react-redux';
import { useThemeSlice } from 'styles/theme/slice';
import { selectThemeKey } from 'styles/theme/slice/selectors';
import { DarkMode, LightMode } from '@mui/icons-material';

export function HomePage() {
  const dispatch = useDispatch();
  const { actions } = useThemeSlice();

  const currentTheme = useSelector(selectThemeKey);

  const darkModeIcon =
    currentTheme === 'dark' ? (
      <LightMode onClick={() => dispatch(actions.changeTheme('light'))} />
    ) : (
      <DarkMode onClick={() => dispatch(actions.changeTheme('dark'))} />
    );

  return (
    <>
      <Helmet>
        <title>Freebets - Plays</title>
        <meta name="description" content="Freebets - Daily Plays" />
      </Helmet>
      <Box sx={{ display: 'flex' }}>
        <CssBaseline />
        <AppBar position="absolute" open={false}>
          <Toolbar
            sx={{
              pr: '24px', // keep right padding when drawer closed
            }}
          >
            <IconButton
              edge="start"
              color="inherit"
              aria-label="open drawer"
              onClick={() => {}}
              sx={{
                marginRight: '36px',
                // ...(false && { display: 'none' }),
              }}
            >
              <MenuIcon />
            </IconButton>
            <Typography
              component="h1"
              variant="h6"
              color="inherit"
              noWrap
              sx={{ flexGrow: 1 }}
            >
              Freebets - Home
            </Typography>
            <IconButton color="inherit">
              <Badge badgeContent={4} color="secondary">
                {darkModeIcon}
              </Badge>
            </IconButton>
          </Toolbar>
          <Box
            component="main"
            sx={{
              backgroundColor: theme =>
                theme.palette.mode === 'light'
                  ? theme.palette.grey[100]
                  : theme.palette.grey[900],
              flexGrow: 1,
              height: '100vh',
              overflow: 'auto',
            }}
          >
            <Toolbar />
            <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
              <Grid container spacing={3}>
                {/* Recent Orders */}
                <Grid item xs={12}>
                  <BetIndex />
                </Grid>
              </Grid>
              <Copyright sx={{ pt: 4 }} />
            </Container>
          </Box>
        </AppBar>
      </Box>
    </>
  );
}
