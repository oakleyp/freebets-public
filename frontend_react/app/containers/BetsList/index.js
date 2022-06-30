import React from 'react';
import PropTypes from 'prop-types';

import List from 'components/List';
import ListItem from 'components/ListItem';
import BetsListItem from 'containers/BetsListItem';
import LoadingIndicator from 'components/LoadingIndicator';
import { getEffectiveTS } from 'utils/bets';

function BetsList({ betsLoading, betsLoadingErr, bets }) {
  if (betsLoading) {
    return <List component={LoadingIndicator} />;
  }

  if (betsLoadingErr) {
    console.log(betsLoadingErr);
    const ErrorComponent = () => (
      <ListItem item="Something went wrong, please try again!" />
    );
    return <List component={ErrorComponent} />;
  }

  if (!bets.singleBets.length && !bets.multiBets.length) {
    return <ListItem item="No results to display" />
  }

  const allBets = [...bets.singleBets, ...bets.multiBets].sort((a, b) => {
    return getEffectiveTS(a) - getEffectiveTS(b)
  });

  if (bets !== null) {
    return <List items={allBets} component={BetsListItem} />;
  }

  return null;
}

BetsList.propTypes = {
  betsLoading: PropTypes.bool,
  betsLoadingErr: PropTypes.any,
  bets: PropTypes.any,
};

export default BetsList;
