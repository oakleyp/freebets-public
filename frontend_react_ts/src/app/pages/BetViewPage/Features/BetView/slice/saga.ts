import { call, put, select, takeLatest, all } from 'redux-saga/effects';

import { request } from 'utils/request';
import { selectBetId } from './selectors';
import { betViewActions as actions } from '.';
import { BetViewResponse } from 'types/Bet';
import { BetViewErrorType } from './types';

export function* getBet() {
  const betId = yield select(selectBetId);
  const requestURL = `http://desktop-ebchtvi/api/v1/bets/${betId}`;

  try {
    // Call our request helper (see 'utils/request')
    const betData: BetViewResponse = yield call(request, requestURL);
    yield put(actions.betLoaded(betData));
  } catch (err: any) {
    if (err.response?.status === 404) {
      yield put(actions.betLoadingError(err));
    } else {
      yield put(actions.betLoadingError(BetViewErrorType.RESPONSE_ERROR));
    }
  }
}

/**
 * Root saga manages watcher lifecycle
 */
export function* betViewSaga() {
  // Watches for LOAD_REPOS actions and calls getRepos when one comes in.
  // By using `takeLatest` only the result of the latest API call is applied.
  // It returns task descriptor (just like fork) so we can continue execution
  // It will be cancelled automatically on component unmount

  yield all([takeLatest(actions.loadBet.type, getBet)]);
}
