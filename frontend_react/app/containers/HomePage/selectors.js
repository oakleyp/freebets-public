/**
 * Homepage selectors
 */

import { createSelector } from 'reselect';
import { initialState } from './reducer';

const selectHome = state => state.home || initialState;
const selectGlobal = state => state;

const makeSelectUsername = () =>
  createSelector(
    selectHome,
    homeState => homeState.username,
  );

const makeSelectBetTypes = () =>
  createSelector(
    selectHome,
    homeState => homeState.betTypes,
  );

export { selectHome, makeSelectUsername, makeSelectBetTypes };
