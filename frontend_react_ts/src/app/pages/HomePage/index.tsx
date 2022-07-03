import * as React from 'react';
import { Helmet } from 'react-helmet-async';

export function HomePage() {
  return (
    <>
      <Helmet>
        <title>Freebets - Plays</title>
        <meta name="description" content="Freebets - Daily Plays" />
      </Helmet>
      <span>Daily Plays</span>
    </>
  );
}
