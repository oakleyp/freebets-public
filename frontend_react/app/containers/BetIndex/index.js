import React, { useState, memo, useEffect } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { compose } from 'redux';
import { createStructuredSelector } from 'reselect';
import { useInjectReducer } from 'utils/injectReducer';
import { useInjectSaga } from 'utils/injectSaga';
import {
  makeSelectBets,
  makeSelectCurrentBetSearchParams,
  makeSelectSelectedBet,
  makeSelectBetsLoading,
  makeSelectBetsLoadingErr,
} from './selectors';

import { setBetSearchParams, loadBets } from './actions';
import reducer from './reducer';
import saga from './saga';

import {
  Button,
  Checkbox,
  Grid,
  Header,
  Icon,
  Image,
  Menu,
  Segment,
  Sidebar,
  Accordion,
  Tab,
} from 'semantic-ui-react';
import BetsList from '../BetsList';
import BetTypeSelectForm from './BetTypeSelectForm';
import StrategiesSelectForm from './StrategiesSelectForm';
import TracksSelectForm from './TracksSelectForm';

const key = 'betindex'

function BetIndex({ betsLoading, betsLoadingErr, bets, onBetFilterSave, currentBetSearchParams, loadBets }) {
  useInjectReducer({ key, reducer });
  useInjectSaga({ key, saga });

  // Bets initial load
  useEffect(() => {
    loadBets();
  }, []);

  const [activeIndex, setActiveIndex] = useState(-1);
  const [menuVisible, setMenuVisible] = useState(false);

  // Local state to hold uncommitted filter changes
  const [betTypes, setBetTypes] = useState(currentBetSearchParams.betTypes || []);
  const [betStrategies, setBetStrategies] = useState(currentBetSearchParams.betStratTypes || []);
  const [trackCodes, setTrackCodes] = useState(currentBetSearchParams.trackCodes || []);

  useEffect(() => {
    setBetTypes(currentBetSearchParams.betTypes || []);
    setBetStrategies(currentBetSearchParams.betStratTypes || []);
    setTrackCodes(currentBetSearchParams.trackCodes || []);
  }, [currentBetSearchParams]);

  const handleTabClick = (e, titleProps) => {
    const { index } = titleProps;
    const newIndex = activeIndex === index ? -1 : index;

    setActiveIndex(newIndex);
  };

  const handleFilterSaveClick = () => {
    onBetFilterSave({
      ...currentBetSearchParams,
      betTypes,
      betStratTypes: betStrategies,
      trackCodes: trackCodes,
    });
  };

  const panes = [
    {
      menuItem: "Today's Bets",
      render: () => null,
    },
    {
      menuItem: 'Upcoming',
      render: () => null,
    },
  ];

  return (
    <>
      <Menu secondary>
        <Menu.Item>
          <Button icon onClick={() => setMenuVisible(!menuVisible)}>
            <Icon name="align justify" />
          </Button>
        </Menu.Item>
        <Menu.Item>
          <Tab menu={{ secondary: true, pointing: true }} panes={panes} />
        </Menu.Item>
      </Menu>

      <Sidebar.Pushable as={Segment} style={{ overflow: 'hidden' }}>
        <Sidebar
          animation="uncover"
          direction="left"
          icon="labeled"
          inverted
          vertical
          visible={menuVisible}
          width="wide"
        >
          <>
          <Accordion as={Menu} vertical fluid>
            <Menu.Item>
              <Accordion.Title
                active={activeIndex === 0}
                content="Strategies"
                index={0}
                onClick={handleTabClick}
              />
              <Accordion.Content
                active={activeIndex === 0}
                content={<StrategiesSelectForm bets={bets} strategies={betStrategies} setStrategies={setBetStrategies} />}
              />
            </Menu.Item>

            <Menu.Item>
              <Accordion.Title
                active={activeIndex === 1}
                content="Bet Types"
                index={1}
                onClick={handleTabClick}
              />
              <Accordion.Content
                active={activeIndex === 1}
                content={<BetTypeSelectForm bets={bets} betTypes={betTypes} setBetTypes={setBetTypes} />}
              />
            </Menu.Item>

            <Menu.Item>
              <Accordion.Title
                active={activeIndex === 2}
                content="Tracks"
                index={2}
                onClick={handleTabClick}
              />
              <Accordion.Content
                active={activeIndex === 2}
                content={<TracksSelectForm bets={bets} enabledTrackCodes={trackCodes} setTrackCodes={setTrackCodes} />}
              />
            </Menu.Item>
          </Accordion>
          <Button primary attached='bottom' onClick={handleFilterSaveClick} loading={betsLoading} disabled={betsLoading}>Save</Button>
          </>
        </Sidebar>

        <Sidebar.Pusher dimmed={menuVisible}>
          <div style={{minHeight: '30em'}}>
            <BetsList
              betsLoading={betsLoading}
              betsLoadingErr={betsLoadingErr}
              bets={bets}
            />
          </div>
        </Sidebar.Pusher>
      </Sidebar.Pushable>
    </>
  );
}

BetIndex.propTypes = {
  currentBetSearchParams: PropTypes.object,
  betsLoading: PropTypes.bool,
  bets: PropTypes.object,
  betsLoadingErr: PropTypes.object,
  selectedBet: PropTypes.object,
};

const mapStateToProps = createStructuredSelector({
  currentBetSearchParams: makeSelectCurrentBetSearchParams(),
  betsLoading: makeSelectBetsLoading(),
  bets: makeSelectBets(),
  betsLoadingErr: makeSelectBetsLoadingErr(),
  selectedBet: makeSelectSelectedBet(),
});

export function mapDispatchToProps(dispatch) {
  return {
    onBetFilterSave: betSearchParams => {
      dispatch(setBetSearchParams(betSearchParams));
    },
    loadBets: () => {
      dispatch(loadBets());
    }
  };
}

const withConnect = connect(
  mapStateToProps,
  mapDispatchToProps,
);

export default compose(
  withConnect,
  memo,
)(BetIndex);
