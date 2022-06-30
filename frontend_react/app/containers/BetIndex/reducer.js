/*
 * AppReducer
 *
 * The reducer takes care of our data. Using actions, we can
 * update our application state. To add a new action,
 * add it to the switch statement in the reducer function
 *
 */

import produce from 'immer';
import {
  LOAD_BETS,
  LOAD_BETS_ERROR,
  LOAD_BETS_SUCCESS,
  SET_BET_SEARCH_PARAMS,
  ALL_TRACKS
} from './constants';

// The initial state of the App
export const initialState = {
  betsLoading: false,
  betsLoadingErr: null,
  currentBetSearchParams: {
    betTypes: null,
    betStratTypes: null,
    limit: 2000,
    skip: 0,
    trackCodes: ALL_TRACKS,
  },
  currentBetsList: {
    singleBets: [],
    multiBets: [],
  },
  selectedBet: null,
};

/* eslint-disable default-case, no-param-reassign */
const appReducer = (state = initialState, action) =>
  produce(state, draft => {
    switch (action.type) {
      case LOAD_BETS:
        draft.betsLoading = true;
        draft.betsLoadingErr = null;
        break;

      case LOAD_BETS_SUCCESS:
        draft.currentBetsList.singleBets = action.singleBets;
        draft.currentBetsList.multiBets = action.multiBets;
        draft.currentBetSearchParams.betStratTypes = action.betStratTypes;
        draft.currentBetSearchParams.betTypes = action.betTypes;
        draft.currentBetSearchParams.trackCodes = action.trackCodes;
        draft.currentBetSearchParams.limit = action.limit;
        draft.currentBetSearchParams.skip = action.skip;
        draft.betsLoading = false;
        break;

      case LOAD_BETS_ERROR:
        draft.error = action.error;
        draft.betsLoading = false;
        break;

      case SET_BET_SEARCH_PARAMS:
        draft.currentBetSearchParams = action.betSearchParams;
        break;
    }
  });

export default appReducer;
