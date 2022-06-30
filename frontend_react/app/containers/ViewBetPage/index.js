/*
 * ViewBetPage
 *
 * Displays info about an individual bet
 */

import React, { useEffect, memo } from 'react';
import PropTypes from 'prop-types';
import { Helmet } from 'react-helmet';
import { connect } from 'react-redux';
import { compose } from 'redux';
import { createStructuredSelector } from 'reselect';

import { useInjectReducer } from 'utils/injectReducer';
import { useInjectSaga } from 'utils/injectSaga';

import {Loader, Dimmer, Message} from 'semantic-ui-react';
import reducer from './reducer';
import saga from './saga';
import { makeSelectBet, makeSelectBetId, makeSelectBetLoading, makeSelectBetLoadingErr, makeSelectBetMetaType } from './selectors';
import { loadBet, setBetId } from './actions';
import SingleBetView from 'components/SingleBetView';
import MultiBetView from 'components/MultiBetView';
import Section from './Section';

const key = 'betview';

export function ViewBetPage({setBetId, loadBet, bet, betLoading, betLoadingErr, betId, match, betMetaType}) {
  const { params } = match;

  useInjectReducer({ key, reducer });
  useInjectSaga({ key, saga });

  useEffect(() => {
    setBetId(params.betId);
  }, []);

  useEffect(() => {
    if (betId) {
      loadBet();
    }
  }, [betId]);

  let content = (
    <Dimmer active inverted>
      <Loader inverted content='Loading...' />
    </Dimmer>
  );

  if (betLoadingErr) {
    content = (
      <Message negative>
        <Message.Header>Something went wrong...</Message.Header>
        <p>Unable to load bet {betId} - {`${betLoadingErr}`}</p>
      </Message>
    )
  } else if (!betLoading && bet) {
    content = betMetaType === 'single' ?
      <SingleBetView bet={bet} /> :
      <MultiBetView bet={bet} />
  }

  return (
    <article>
      <Helmet>
        <title>{`Freebets - Bet ${params.betId}`}</title>
        <meta name="description" content="Keeneland Free Bets" />
      </Helmet>
      <div>
        <Section>
          {content}
        </Section>
      </div>
    </article>
  );
}

ViewBetPage.propTypes = {
  setBetId: PropTypes.func,
  loadBet: PropTypes.func,
  bet: PropTypes.object,
  betLoading: PropTypes.bool,
  betLoadingErr: PropTypes.object,
  betId: PropTypes.string,
  betMetaType: PropTypes.string,
};

ViewBetPage.defaultProps = {
};

const mapStateToProps = createStructuredSelector({
  betId: makeSelectBetId(),
  betLoading: makeSelectBetLoading(),
  betLoadingErr: makeSelectBetLoadingErr(),
  bet: makeSelectBet(),
  betMetaType: makeSelectBetMetaType(),
});

export function mapDispatchToProps(dispatch) {
  return {
    setBetId: id => dispatch(setBetId(id)),
    loadBet: () => dispatch(loadBet()),
  };
}

const withConnect = connect(
  mapStateToProps,
  mapDispatchToProps,
);

export default compose(
  withConnect,
  memo,
)(ViewBetPage);
