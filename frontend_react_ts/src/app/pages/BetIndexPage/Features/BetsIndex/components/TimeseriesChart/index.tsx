import React, { useEffect, useMemo, useState } from 'react';
import {
  Charts,
  ChartContainer,
  ChartRow,
  YAxis,
  BandChart,
  styler,
  Resizable,
  ScatterChart,
} from 'react-timeseries-charts';
// Typescript definition is missing some exports in library
// @ts-ignore
import { TimeSeries, percentile, avg } from 'pondjs';
import { format } from 'd3-format';

import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import { getEffectiveTS } from 'utils/bets';

dayjs.extend(utc);
dayjs.extend(timezone);

interface TimeseriesChartProps {
  bets: any[];
  onSelection?: Function | null;
}

export function TimeseriesChart({
  bets,
  onSelection = () => {},
}: TimeseriesChartProps) {
  const tzGuess = dayjs.tz.guess();

  // function getTouchFrame() {
  //   return document.getElementById("chart-cont");
  // }

  // function isEventInElement(event, element)   {
  //     var rect = element.getBoundingClientRect();
  //     console.log({rect});
  //     var x = event.clientX;
  //     if (x < rect.left || x >= rect.right) return false;
  //     var y = event.clientY;
  //     if (y < rect.top || y >= rect.bottom) return false;
  //     return true;
  // }

  // function onTouchStart(e) {
  //   console.log('touchstart', {e});
  //   if (isEventInElement(e, getTouchFrame())) {
  //     console.log('inframe');
  //     e.preventDefault();
  //   }
  // }

  // function onTouchEnd(e) {
  //   if (isEventInElement(e, getTouchFrame())) {
  //     e.preventDefault();
  //   }
  // }

  // useEffect(() => {
  //   window.addEventListener('touchstart', onTouchStart, {passive: false});
  //   window.addEventListener('touchstart', onTouchEnd, {passive: false});

  //   return () => {
  //     window.removeEventListener('touchstart', onTouchStart);
  //     window.removeEventListener('touchend', onTouchEnd);
  //   }
  // })

  const betMetaMap = useMemo(
    () =>
      bets.reduce(
        (res, bet) => ({
          ...res,
          [bet.id]: {
            dayjsInst: dayjs.utc(getEffectiveTS(bet)),
            betInst: bet,
          },
        }),
        {},
      ),
    [bets],
  );

  function getBetFromPoint(point: any): any {
    const betId = point.event.data().get('bet_id');
    const bet = betMetaMap[betId].betInst;

    return bet;
  }

  const points = useMemo(
    () =>
      [...bets]
        .sort(
          (a, b) =>
            betMetaMap[a.id].dayjsInst.tz(tzGuess).toDate() -
            betMetaMap[b.id].dayjsInst.tz(tzGuess).toDate(),
        )
        .map(bet => [
          betMetaMap[bet.id].dayjsInst.tz(dayjs.tz.guess()).toDate(),
          bet.avg_reward / bet.cost,
          bet.id,
        ]),
    [bets, tzGuess, betMetaMap],
  );

  const series = new TimeSeries({
    name: 'Bet',
    columns: ['time', 'ratio', 'bet_id'],
    points,
  });

  const [tracker, setTracker] = useState(null);
  const [timerange, setTimerange] = useState(series.timerange());
  const [highlight, setHighlight] = useState<any | null>(null);
  const [selection, setSelection] = useState(null);

  const formatter = format('.2f');
  let text = `Avg. Reward / Cost Ratio: -, time: -:--`;
  let infoValues: any[] = [];
  if (highlight) {
    const speedText = `${formatter(highlight.event.get(highlight.column))}`;
    text = `
                Avg. Reward / Cost Ratio: ${speedText},
                time: ${highlight.event.timestamp().toLocaleTimeString()}
            `;

    const bet = getBetFromPoint(highlight);

    infoValues = [
      { label: 'Ratio', value: speedText },
      { label: 'Track', value: bet.race.track_code.toUpperCase() },
    ];
  }

  const bandStyle = styler([
    { key: 'ratio', color: 'blue', width: 1, opacity: 0.5 },
  ]);

  /* const heat = [
            "#023858",
            "#045a8d",
            "#0570b0",
            "#3690c0",
            "#74a9cf",
            "#a6bddb",
            "#d0d1e6",
            "#ece7f2",
            "#fff7fb"
        ]; */

  const perEventStyle = (column, event) => {
    const color = 'steelblue'; // heat[Math.floor((1 - event.get("station1") / 40) * 9)];
    return {
      normal: {
        fill: color,
        opacity: 1.0,
      },
      highlighted: {
        fill: color,
        stroke: 'none',
        opacity: 1.0,
        cursor: 'pointer',
      },
      selected: {
        fill: 'none',
        stroke: '#2CB1CF',
        strokeWidth: 3,
        opacity: 1.0,
      },
      muted: {
        stroke: 'none',
        opacity: 0.4,
        fill: color,
      },
    };
  };

  const timeAxisStyle = {
    values: { valueColor: 'Green', valueWeight: 200, valueSize: 12 },
  };

  const YAxisStyle = {
    axis: { axisColor: '#C0C0C0' },
    label: { labelColor: 'Blue', labelWeight: 100, labelSize: 12 },
    values: { valueSize: 12 },
  };

  const handleSelectionChanged = point => {
    setSelection(point);

    if (typeof onSelection === 'function') {
      onSelection(getBetFromPoint(point));
    }
  };

  const handleMouseNear = point => {
    setHighlight(point);
  };

  return (
    <div>
      <div className="row">
        <div className="col-md-12">{text}</div>
      </div>

      <hr />

      <div id="chart-cont" className="row">
        <div className="col-md-12">
          <Resizable>
            <ChartContainer
              timeRange={timerange}
              timeAxisStyle={timeAxisStyle}
              trackerPosition={tracker}
              trackerStyle={{
                box: {
                  fill: 'black',
                  color: '#DDD',
                },
                line: {
                  stroke: 'red',
                  strokeDasharray: 2,
                },
              }}
              maxTime={series.timerange().end()}
              minTime={series.timerange().begin()}
              enablePanZoom={true}
              enableDragZoom={true}
              onBackgroundClick={() => setSelection(null)}
              onTimeRangeChanged={timerange => setTimerange(timerange)}
              onTrackerChanged={tracker => setTracker(tracker)}
            >
              <ChartRow
                height="150"
                debug={false}
                trackerInfoWidth={125}
                trackerInfoHeight={40}
                trackerInfoValues={infoValues}
              >
                <YAxis
                  id="ratio"
                  label="Avg. Reward / Cost Ratio"
                  labelOffset={-5}
                  min={0}
                  max={series.max('ratio')}
                  style={YAxisStyle}
                  width="70"
                  type="linear"
                  format=",.1f"
                />
                <Charts>
                  <BandChart
                    axis="ratio"
                    series={series}
                    style={bandStyle}
                    column="ratio"
                    aggregation={{
                      size: '2m',
                      reducers: {
                        outer: [percentile(5), percentile(95)],
                        inner: [percentile(25), percentile(75)],
                      },
                    }}
                    interpolation="curveBasis"
                  />
                  <ScatterChart
                    axis="ratio"
                    series={series}
                    columns={['ratio']} // {["station1", "station2"]}
                    style={perEventStyle}
                    // info={infoValues}
                    // infoHeight={28}
                    // infoWidth={110}
                    // infoOffsetY={10}
                    // infoStyle={{ box: {
                    //     fill: "black",
                    //     color: "#DDD"
                    // }}}
                    format=".1f"
                    selected={selection}
                    onSelectionChange={p => handleSelectionChanged(p)}
                    onMouseNear={p => handleMouseNear(p)}
                    highlight={highlight}
                    radius={(event, column) =>
                      window.screen.width >= 768 ? 3 : 5
                    }
                  />
                </Charts>
              </ChartRow>
            </ChartContainer>
          </Resizable>
        </div>
      </div>
    </div>
  );
}
