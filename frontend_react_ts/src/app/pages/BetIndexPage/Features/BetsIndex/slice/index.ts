import { PayloadAction } from '@reduxjs/toolkit';
import { BetsListResponse } from 'types/Bet';
import { createSlice } from 'utils/@reduxjs/toolkit';
import { useInjectReducer, useInjectSaga } from 'utils/redux-injectors';
import { betsIndexSaga } from './saga';
import { BetsIndexState, BetsErrorType, BetSearchParams } from './types';

export const initialState: BetsIndexState = {
  currentBetList: {
    singleBets: [],
    multiBets: [],
  },
  loading: false,
  error: null,
  availableFilterValues: {
    trackCodes: [],
    betTypes: [],
    betStratTypes: [],
  },
  currentBetSearchParams: {
    betTypes: null,
    betStratTypes: null,
    limit: 2000,
    skip: 0,
    trackCodes: [], // TODO
  },
  selectedBet: null,
  nextRefreshTs: null,
  countdownRefreshEnabled: false,
};

const slice = createSlice({
  name: 'betsIndex',
  initialState,
  reducers: {
    loadBets(state) {
      state.loading = true;
      state.error = null;
      state.countdownRefreshEnabled = false;
    },
    betsLoaded(state, action: PayloadAction<BetsListResponse>) {
      const resp = action.payload;
      state.currentBetList.singleBets = resp.single_bets;
      state.currentBetList.multiBets = resp.multi_bets;
      state.currentBetSearchParams.betStratTypes = resp.bet_strat_types;
      state.currentBetSearchParams.betTypes = resp.bet_types;
      // Only add previously unseen track codes to default filter
      state.currentBetSearchParams.trackCodes = [
        ...new Set([
          ...resp.track_codes,
          ...resp.all_track_codes.filter(
            tc => !state.availableFilterValues.trackCodes.includes(tc),
          ),
        ]),
      ];
      state.currentBetSearchParams.limit = resp.limit;
      state.currentBetSearchParams.skip = resp.skip;
      state.availableFilterValues.trackCodes = resp.all_track_codes;
      state.availableFilterValues.betTypes = resp.all_bet_types;
      state.availableFilterValues.betStratTypes = resp.all_bet_strat_types;
      state.nextRefreshTs = resp.next_refresh_ts;
      state.loading = false;
      state.countdownRefreshEnabled = true;
    },
    betsLoadingError(state, action: PayloadAction<BetsErrorType>) {
      state.error = action.payload;
      state.nextRefreshTs = null;
      state.loading = false;
      state.countdownRefreshEnabled = false;
      state.currentBetSearchParams = initialState.currentBetSearchParams;
    },
    setBetSearchParams(state, action: PayloadAction<BetSearchParams>) {
      state.currentBetSearchParams = action.payload;
    },
    setCountdownRefreshEnabled(state, action: PayloadAction<boolean>) {
      state.countdownRefreshEnabled = action.payload;
    },
  },
});

export const { actions: betsIndexActions, reducer } = slice;

export const useBetIndexSlice = () => {
  useInjectReducer({ key: slice.name, reducer: slice.reducer });
  useInjectSaga({ key: slice.name, saga: betsIndexSaga });
  return { actions: slice.actions };
};
