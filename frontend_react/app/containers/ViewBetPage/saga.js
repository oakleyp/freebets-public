
import { call, put, select, takeLatest, all } from 'redux-saga/effects';

import request from 'utils/request';
import { betLoaded, betLoadedError } from './actions';
import { makeSelectBetId } from './selectors';
import { LOAD_BET } from './constants';

export function* getBet() {
  const betId = yield select(makeSelectBetId());
  const requestURL = `http://${process.env.API_URL}/v1/bets/${betId}`;

  try {
    // Call our request helper (see 'utils/request')
    const betData = yield call(request, requestURL);
    yield put(betLoaded(betData));
  } catch (err) {
    yield put(betLoadedError(err));
  }
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
    takeLatest(LOAD_BET, getBet),
  ]);
}
