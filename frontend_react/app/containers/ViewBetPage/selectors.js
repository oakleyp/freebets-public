/**
 * ViewBetPage selectors
 */

import { createSelector } from 'reselect';
import { initialState } from './reducer';

const selectBetView = state => state.betview || initialState;
const selectGlobal = state => state;

const makeSelectBetId = () =>
  createSelector(
    selectBetView,
    betViewState => betViewState.betId,
  );

const makeSelectBet = () =>
  createSelector(
    selectBetView,
    betViewState => betViewState.bet,
  );

const makeSelectBetLoading = () =>
  createSelector(
    selectBetView,
    betViewState => betViewState.betLoading,
  );

const makeSelectBetLoadingErr = () =>
  createSelector(
    selectBetView,
    betViewState => betViewState.betLoadingErr,
  );

const makeSelectBetMetaType = () =>
  createSelector(
    selectBetView,
    betViewState => betViewState.betMetaType,
  );

export { selectBetView, makeSelectBetId, makeSelectBet, makeSelectBetMetaType, makeSelectBetLoadingErr, makeSelectBetLoading };
