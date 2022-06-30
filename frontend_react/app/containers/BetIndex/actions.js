import {
  LOAD_BETS,
  LOAD_BETS_ERROR,
  LOAD_BETS_SUCCESS,
  SET_BET_SEARCH_PARAMS,
} from './constants';


/**
 * Load all bets with the currentBetSearchParams
 */
export function loadBets() {
  return {
    type: LOAD_BETS,
  };
}
/**
 * Action called once bets have been loaded successfully
 * @param {Object} betResult - result from the /bets endpoint
 * @returns null
 */
export function betsLoaded(betResult) {
  return {
    type: LOAD_BETS_SUCCESS,
    singleBets: betResult.single_bets,
    multiBets: betResult.multi_bets,
    skip: betResult.skip,
    limit: betResult.limit,
    trackCodes: betResult.track_codes,
    betTypes: betResult.bet_types,
    betStratTypes: betResult.bet_strat_types,
  };
}

/**
 *
 * @param {Object} error - The
 * @returns
 */
export function betsLoadedError(error) {
  return {
    type: LOAD_BETS_ERROR,
    error,
  };
}

export function setBetSearchParams(betSearchParams) {
  return {
    type: SET_BET_SEARCH_PARAMS,
    betSearchParams,
  }
}
