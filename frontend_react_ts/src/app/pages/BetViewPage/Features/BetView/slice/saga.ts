import { call, put, select, takeLatest, all } from 'redux-saga/effects';

import { request } from 'utils/request';
import { selectBetId } from './selectors';
import { betViewActions as actions } from '.';
import { BetViewResponse } from 'types/Bet';
import { BetViewErrorType } from './types';

export function* getBet() {
  const betId = yield select(selectBetId);
  const requestURL = `${process.env.REACT_APP_API_URL}/api/v1/bets/${betId}`;

  try {
    // Call our request helper (see 'utils/request')
    const betData: BetViewResponse = yield call(request, requestURL);
    yield put(actions.betLoaded(betData));
  } catch (err: any) {
    if (err.response?.status === 404) {
      yield put(actions.betLoadingError(BetViewErrorType.NOT_FOUND_ERROR));
    } else {
      yield put(actions.betLoadingError(BetViewErrorType.RESPONSE_ERROR));
    }
  }
}

/**
 * Root saga manages watcher lifecycle
 */
export function* betViewSaga() {
  yield all([takeLatest(actions.loadBet.type, getBet)]);
}
