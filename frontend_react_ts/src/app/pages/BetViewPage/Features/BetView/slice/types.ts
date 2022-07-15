import { SingleBet, MultiBet } from 'types/Bet';

export type BetViewState = {
  betId?: string | null;
  loading: boolean;
  error?: BetViewErrorType | null;
  bet?: SingleBet | MultiBet | null;
  betMetaType?: string | null;
  nextRefreshTs?: number | null;
};

export enum BetViewErrorType {
  RESPONSE_ERROR = 1,
  NOT_FOUND_ERROR = 2,
}
