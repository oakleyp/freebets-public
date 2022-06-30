import {
  SET_BET_ID,
  LOAD_BET,
  LOAD_BET_ERROR,
  LOAD_BET_SUCCESS,
} from './constants';


/**
 * Load all bets with the currentBetSearchParams
 */
export function loadBet() {
  return {
    type: LOAD_BET,
  };
}
/**
 * Action called once bets have been loaded successfully
 * @param {Object} betResult - result from the /bets endpoint
 * @returns null
 */
export function betLoaded(betResult) {
  return {
    type: LOAD_BET_SUCCESS,
    bet: betResult.data,
    betMetaType: betResult.result_type,
  };
}

/**
 * Action called when bet loading fails.
 * @param {Object} error
 * @returns
 */
export function betLoadedError(error) {
  return {
    type: LOAD_BET_ERROR,
    error,
  };
}

export function setBetId(id) {
  return {
    type: SET_BET_ID,
    id,
  }
}
