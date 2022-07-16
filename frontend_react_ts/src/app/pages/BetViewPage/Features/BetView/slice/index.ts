import { PayloadAction } from '@reduxjs/toolkit';
import { BetViewResponse } from 'types/Bet';
import { createSlice } from 'utils/@reduxjs/toolkit';
import { useInjectReducer, useInjectSaga } from 'utils/redux-injectors';
import { betViewSaga } from './saga';
import { BetViewState, BetViewErrorType } from './types';

export const initialState: BetViewState = {
  betId: null,
  loading: false,
  error: null,
  bet: null,
  betMetaType: null,
  nextRefreshTs: null,
  loadingBackground: false,
  betBackground: null,
  errorBackground: null,
};

const slice = createSlice({
  name: 'betView',
  initialState,
  reducers: {
    setBetId(state, action: PayloadAction<string>) {
      state.betId = action.payload;
    },
    loadBet(state) {
      state.loading = true;
      state.error = null;
    },
    betLoaded(state, action: PayloadAction<BetViewResponse>) {
      const resp = action.payload;
      state.bet = resp.data;
      state.betBackground = resp.data;
      state.betMetaType = resp.result_type;
      state.nextRefreshTs = resp.next_refresh_ts;
      state.loading = false;
    },
    betLoadingError(state, action: PayloadAction<BetViewErrorType>) {
      state.error = action.payload;
      state.loading = false;
    },
    loadBetBackground(state) {
      state.loadingBackground = true;
      state.errorBackground = null;
    },
    betLoadedBackground(state, action: PayloadAction<BetViewResponse>) {
      const resp = action.payload;
      state.betBackground = resp.data;
      state.nextRefreshTs = resp.next_refresh_ts;
      state.loadingBackground = false;
    },
    betLoadingErrorBackground(state, action: PayloadAction<BetViewErrorType>) {
      state.errorBackground = action.payload;
      state.loadingBackground = false;
    },
    swapToForeground(state) {
      state.bet = state.betBackground;
    },
  },
});

export const { actions: betViewActions, reducer } = slice;

export const useBetViewSlice = () => {
  useInjectReducer({ key: slice.name, reducer: slice.reducer });
  useInjectSaga({ key: slice.name, saga: betViewSaga });
  return { actions: slice.actions };
};
