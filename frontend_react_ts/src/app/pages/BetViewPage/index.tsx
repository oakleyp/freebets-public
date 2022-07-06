import * as React from 'react';
import Grid from '@mui/material/Grid';
import { Copyright } from 'app/components/Copyright';
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
