import produce from 'immer';
import {
  SET_BET_ID,
  LOAD_BET,
  LOAD_BET_ERROR,
  LOAD_BET_SUCCESS,
} from './constants';

export const initialState = {
  betId: null,
  betLoading: false,
  betLoadingErr: null,
  bet: null,
  betMetaType: null,
};

/* eslint-disable default-case, no-param-reassign */
const viewBetPageReducer = (state = initialState, action) =>
  produce(state, draft => {
    switch (action.type) {
      case SET_BET_ID:
        draft.betId = action.id
        break;

      case LOAD_BET:
        draft.betLoading = true;
        draft.betLoadingErr = null;
        break;

      case LOAD_BET_SUCCESS:
        draft.bet = action.bet;
        draft.betMetaType = action.betMetaType;
        draft.betLoading = false;
        break;

      case LOAD_BET_ERROR:
        draft.betLoadingErr = action.error;
        draft.betLoading = false;
        break;
    }
  });

export default viewBetPageReducer;
