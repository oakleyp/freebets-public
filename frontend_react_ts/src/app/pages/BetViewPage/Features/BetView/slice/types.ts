import { SingleBet, MultiBet } from 'types/Bet';

export type BetViewState = {
  betId?: string | null;
  loading: boolean;
  error?: BetViewErrorType | null;
  bet?: SingleBet | MultiBet | null;
  betMetaType?: string | null;
  nextRefreshTs?: number | null;
  loadingBackground: boolean;
  betBackground?: SingleBet | MultiBet | null;
  errorBackground?: BetViewErrorType | null;
};

export interface BetDiffDescriptor {
  minRewardDiff: number;
  avgRewardDiff: number;
  maxRewardDiff: number;
}

export function getBetDiff(
  base: SingleBet | MultiBet,
  current: SingleBet | MultiBet,
): BetDiffDescriptor {
  return {
    minRewardDiff: +(current.min_reward - base.min_reward).toFixed(2),
    avgRewardDiff: +(current.avg_reward - base.avg_reward).toFixed(2),
    maxRewardDiff: +(current.max_reward - base.max_reward).toFixed(2),
  };
}

export enum BetViewErrorType {
  RESPONSE_ERROR = 1,
  NOT_FOUND_ERROR = 2,
}
