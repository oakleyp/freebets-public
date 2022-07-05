import { AppBar } from 'app/components/AppBar/Loadable';
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
import { BetView } from './Features/BetView';
import { PageWrapper } from 'app/components/PageWrapper';

export function BetViewPage({ match }) {
  const { params } = match;

  return (
    <PageWrapper>
      <Grid container spacing={3}>
        {/* Bet View */}
        <Grid item xs={12}>
          <BetView betId={params.betId} />
        </Grid>
      </Grid>
      <Copyright sx={{ pt: 4 }} />
    </PageWrapper>
  );
}
