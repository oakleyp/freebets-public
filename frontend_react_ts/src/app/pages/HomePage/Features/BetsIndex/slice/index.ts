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
  currentBetSearchParams: {
    betTypes: null,
    betStratTypes: null,
    limit: 2000,
    skip: 0,
    trackCodes: ['gcv'], // TODO
  },
  selectedBet: null,
};

const slice = createSlice({
  name: 'betsIndex',
  initialState,
  reducers: {
    loadBets(state) {
      state.loading = true;
      state.error = null;
    },
    betsLoaded(state, action: PayloadAction<BetsListResponse>) {
      const resp = action.payload;
      state.currentBetList.singleBets = resp.single_bets;
      state.currentBetList.multiBets = resp.multi_bets;
      state.currentBetSearchParams.betStratTypes = resp.bet_strat_types;
      state.currentBetSearchParams.betTypes = resp.bet_types;
      state.currentBetSearchParams.trackCodes = resp.track_codes;
      state.currentBetSearchParams.limit = resp.limit;
      state.currentBetSearchParams.skip = resp.skip;
      state.loading = false;
    },
    betsLoadingError(state, action: PayloadAction<BetsErrorType>) {
      state.error = action.payload;
      state.loading = false;
    },
    setBetSearchParams(state, action: PayloadAction<BetSearchParams>) {
      state.currentBetSearchParams = action.payload;
    },
  },
});

export const { actions: betsIndexActions, reducer } = slice;

export const useBetIndexSlice = () => {
  useInjectReducer({ key: slice.name, reducer: slice.reducer });
  useInjectSaga({ key: slice.name, saga: betsIndexSaga });
  return { actions: slice.actions };
};
