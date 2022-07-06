import { BetIndex } from './Features/BetsIndex';
import * as React from 'react';
import { Helmet } from 'react-helmet-async';
import Grid from '@mui/material/Grid';
import { Copyright } from 'app/components/Copyright';
import { PageWrapper } from 'app/components/PageWrapper';

export function BetIndexPage() {
  return (
    <>
      <Helmet>
        <title>Plays</title>
        <meta name="description" content="Freebets - Daily Plays" />
      </Helmet>
      <PageWrapper>
        <Grid container spacing={3}>
          {/* Bet Index */}
          <Grid item xs={12}>
            {/* <img src={headerImage} alt="" style={{ width: '100%' }} /> */}
            <BetIndex />
          </Grid>
        </Grid>
        <Copyright sx={{ pt: 4 }} />
      </PageWrapper>
    </>
  );
}
