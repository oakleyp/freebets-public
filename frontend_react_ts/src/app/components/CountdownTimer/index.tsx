import React, { useState, useEffect } from 'react';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';

dayjs.extend(utc);

interface CountdownTimerProps {
  timeMillis: number;
  endText?: string | null;
  onEnd?: Function | null;
  running?: boolean | null;
}

export function CountdownTimer({
  timeMillis,
  onEnd = () => {},
  endText = 'OFF',
  running = true,
}: CountdownTimerProps) {
  const calculateTimeLeft = () => {
    const difference = dayjs.utc(timeMillis).diff(dayjs().utc());
    let timeLeft = {};

    if (difference > 0) {
      timeLeft = {
        // days: Math.floor(difference / (1000 * 60 * 60 * 24)),
        hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((difference / 1000 / 60) % 60),
        seconds: Math.floor((difference / 1000) % 60),
      };
    }

    return timeLeft;
  };

  const [timeLeft, setTimeLeft] = useState(calculateTimeLeft());

  useEffect(() => {
    if (running) {
      setTimeout(() => {
        setTimeLeft(calculateTimeLeft());
      }, 1000);
    }
  });

  useEffect(() => {
    if (running && Object.keys(timeLeft).every(key => !timeLeft[key])) {
      if (typeof onEnd === 'function') {
        onEnd();
      }
    }
  }, [timeLeft, onEnd, running]);

  let timerComponents: JSX.Element[] = [];

  Object.keys(timeLeft).forEach((interval, i) => {
    timerComponents.push(
      <span>
        {String(timeLeft[interval]).padStart(2, '0')}
        {i < Object.keys(timeLeft).length - 1 && ':'}
      </span>,
    );
  });

  return <>{timerComponents.length ? timerComponents : endText}</>;
}
