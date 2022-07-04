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
      state.betMetaType = resp.result_type;
      state.loading = false;
    },
    betLoadingError(state, action: PayloadAction<BetViewErrorType>) {
      state.error = action.payload;
      state.loading = false;
    },
  },
});

export const { actions: betViewActions, reducer } = slice;

export const useBetViewSlice = () => {
  useInjectReducer({ key: slice.name, reducer: slice.reducer });
  useInjectSaga({ key: slice.name, saga: betViewSaga });
  return { actions: slice.actions };
};
