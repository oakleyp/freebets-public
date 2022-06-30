/**
 * The global state selectors
 */

 import { createSelector } from 'reselect';
 import { initialState } from './reducer';

 const selectGlobal = state => state.global;
 const selectBetIndex = state => state.betindex || initialState;


 const makeSelectBets = () =>
   createSelector(
      selectBetIndex,
      betIndexState => betIndexState.currentBetsList,
   );

 const makeSelectSelectedBet = () =>
   createSelector(
      selectBetIndex,
      betIndexState => betIndexState.selectedBet,
   );

 const makeSelectBetsLoading = () =>
   createSelector(
      selectBetIndex,
      betIndexState => betIndexState.betsLoading,
   );

 const makeSelectBetsLoadingErr = () =>
   createSelector(
      selectBetIndex,
      betIndexState => betIndexState.betsLoadingErr,
   );

 const makeSelectCurrentBetSearchParams = () =>
   createSelector(
      selectBetIndex,
      betIndexState => betIndexState.currentBetSearchParams,
   );

 export {
   selectBetIndex,
   makeSelectBets,
   makeSelectSelectedBet,
   makeSelectBetsLoading,
   makeSelectBetsLoadingErr,
   makeSelectCurrentBetSearchParams,
 };
