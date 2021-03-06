import { createSelector } from '@reduxjs/toolkit';

import { RootState } from 'types';
import { initialState } from '.';

const selectDomain = (state: RootState) => state.betsIndex || initialState;

export const selectBets = createSelector(
  [selectDomain],
  betIndexState => betIndexState.currentBetList,
);

export const selectSelectedBet = createSelector(
  [selectDomain],
  betIndexState => betIndexState.selectedBet,
);

export const selectLoading = createSelector(
  [selectDomain],
  betIndexState => betIndexState.loading,
);

export const selectError = createSelector(
  [selectDomain],
  betIndexState => betIndexState.error,
);

export const selectCurrentBetSearchParams = createSelector(
  [selectDomain],
  betIndexState => betIndexState.currentBetSearchParams,
);

export const selectAvailableFilterValues = createSelector(
  [selectDomain],
  betIndexState => betIndexState.availableFilterValues,
);

export const selectNextRefreshTs = createSelector(
  [selectDomain],
  betIndexState => betIndexState.nextRefreshTs,
);

export const selectCountdownRefreshEnabled = createSelector(
  [selectDomain],
  betIndexState => betIndexState.countdownRefreshEnabled,
);
