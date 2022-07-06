/**
 * Asynchronously loads the component for BetViewPage
 */

import { lazyLoad } from 'utils/loadable';

export const BetViewPage = lazyLoad(
  () => import('./index'),
  module => module.BetViewPage,
);
