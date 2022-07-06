/**
 * Asynchronously loads the component for BetIndexPage
 */

import { lazyLoad } from 'utils/loadable';

export const BetIndexPage = lazyLoad(
  () => import('./index'),
  module => module.BetIndexPage,
);
