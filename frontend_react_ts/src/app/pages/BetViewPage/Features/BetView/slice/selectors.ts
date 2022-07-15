import { createSelector } from '@reduxjs/toolkit';

import { RootState } from 'types';
import { initialState } from '.';

const selectDomain = (state: RootState) => state.betView || initialState;

export const selectBetId = createSelector(
  [selectDomain],
  betViewState => betViewState.betId,
);

export const selectBet = createSelector(
  [selectDomain],
  betViewState => betViewState.bet,
);

export const selectLoading = createSelector(
  [selectDomain],
  betViewState => betViewState.loading,
);

export const selectError = createSelector(
  [selectDomain],
  betViewState => betViewState.error,
);

export const selectBetMetaType = createSelector(
  [selectDomain],
  betViewState => betViewState.betMetaType,
);

export const selectNextRefreshTs = createSelector(
  [selectDomain],
  betViewState => betViewState.nextRefreshTs,
);
