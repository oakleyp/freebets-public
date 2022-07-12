/**
 * Get the effective post_time_stamp of a given bet.
 *
 * @param {Object} bet
 * @returns
 */
export function getEffectiveTS(bet): number {
  if (bet.sub_bets) {
    const earliestPostTime = Math.min(
      ...bet.sub_bets.flatMap(b => b.race.post_time_stamp || Infinity),
    );
    return earliestPostTime === Infinity ? 0 : earliestPostTime;
  }

  return bet.race.post_time_stamp || 0;
}
