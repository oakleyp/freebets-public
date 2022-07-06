import { call, put, select, takeLatest, all } from 'redux-saga/effects';
import { request } from 'utils/request';
import { selectCurrentBetSearchParams } from './selectors';
import { BetsListResponse } from 'types/Bet';
import { betsIndexActions as actions } from '.';
import { BetsErrorType } from './types';

export function* getBetsList() {
  const betParams = yield select(selectCurrentBetSearchParams);

  const paramMapping = {
    bet_types:
      betParams.betTypes &&
      betParams.betTypes.map(encodeURIComponent).join(','),
    bet_strat_types:
      betParams.betStratTypes &&
      betParams.betStratTypes.map(encodeURIComponent).join(','),
    skip: betParams.skip,
    limit: betParams.limit,
    track_codes:
      betParams.trackCodes &&
      betParams.trackCodes.map(encodeURIComponent).join(','),
  };

  // TODO op use env url base
  const reqUrl =
    `${process.env.REACT_APP_API_URL}/api/v1/bets?` +
    Object.entries(paramMapping)
      .reduce(
        (tokenlist: string[], [token, val]) =>
          ![null, undefined].includes(val)
            ? [...tokenlist, `${token}=${val}`]
            : tokenlist,
        [],
      )
      .join('&');

  try {
    const betResult: BetsListResponse = yield call(request, reqUrl);
    if (betResult?.single_bets.length > 0 || betResult.multi_bets.length > 0) {
      yield put(actions.betsLoaded(betResult));
    } else {
      yield put(actions.betsLoadingError(BetsErrorType.NO_BETS_ERROR));
    }
  } catch (err) {
    yield put(actions.betsLoadingError(BetsErrorType.RESPONSE_ERROR));
  }
}

export function* reloadWithCurrentBetSearchParams() {
  yield put(actions.loadBets());
}

/**
 * Root saga manages watcher lifecycle
 */
export function* betsIndexSaga() {
  yield all([
    takeLatest(actions.loadBets.type, getBetsList),
    takeLatest(
      actions.setBetSearchParams.type,
      reloadWithCurrentBetSearchParams,
    ),
  ]);
}
