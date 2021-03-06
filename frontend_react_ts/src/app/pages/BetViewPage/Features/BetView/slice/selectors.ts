import { createSelector } from '@reduxjs/toolkit';

import { RootState } from 'types';
import { initialState } from '.';
import { getBetDiff } from './types';

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

export const selectBetBackground = createSelector(
  [selectDomain],
  betViewState => betViewState.betBackground,
);

export const selectLoadingBackground = createSelector(
  [selectDomain],
  betViewState => betViewState.loadingBackground,
);

export const selectErrorBackground = createSelector(
  [selectDomain],
  betViewState => betViewState.errorBackground,
);

export const selectBetDiff = createSelector(
  [selectBet, selectBetBackground],
  (bet, betBackground) => {
    if (!bet || !betBackground) {
      return;
    }

    return getBetDiff(bet, betBackground);
  },
);
