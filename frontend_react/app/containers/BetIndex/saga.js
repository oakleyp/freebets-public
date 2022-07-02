import { call, put, select, takeLatest, all } from 'redux-saga/effects';
import { LOAD_BETS, SET_BET_SEARCH_PARAMS } from 'containers/BetIndex/constants';

import request from 'utils/request';
import { makeSelectCurrentBetSearchParams } from 'containers/BetIndex/selectors';
import { loadBets, betsLoaded, betsLoadedError } from 'containers/BetIndex/actions';


export function* getBetsList() {
  const betParams = yield select(makeSelectCurrentBetSearchParams());

  const paramMapping = {
    bet_types: betParams.betTypes && betParams.betTypes.map(encodeURIComponent).join(','),
    bet_strat_types: betParams.betStratTypes && betParams.betStratTypes.map(encodeURIComponent).join(','),
    skip: betParams.skip,
    limit: betParams.limit,
    track_codes: betParams.trackCodes && betParams.trackCodes.map(encodeURIComponent).join(','),
  };

  // TODO op use env url base
  const reqUrl = `http://${process.env.API_URL}/api/v1/bets?` +
    Object.entries(paramMapping)
      .reduce((tokenlist, [token, val]) =>
        ![null, undefined].includes(val) ?
          [...tokenlist, `${token}=${val}`] :
          tokenlist,
        [])
      .join('&');

  try {
    const betResult = yield call(request, reqUrl);
    yield put(betsLoaded(betResult));
  } catch (err) {
    yield put(betsLoadedError(err));
  }

}

export function* reloadWithCurrentBetSearchParams() {
  yield put(loadBets())
}

/**
 * Root saga manages watcher lifecycle
 */
export default function* rootSaga() {
  // Watches for LOAD_REPOS actions and calls getRepos when one comes in.
  // By using `takeLatest` only the result of the latest API call is applied.
  // It returns task descriptor (just like fork) so we can continue execution
  // It will be cancelled automatically on component unmount

  yield all([
    takeLatest(LOAD_BETS, getBetsList),
    takeLatest(SET_BET_SEARCH_PARAMS, reloadWithCurrentBetSearchParams),
  ]);
}
