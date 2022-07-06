import React, { useState, useEffect } from 'react';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';

dayjs.extend(utc);

interface PostTimerProps {
  postTime: number;
}

export function PostTimer({ postTime }: PostTimerProps) {
  console.log({ postTime });

  const calculateTimeLeft = () => {
    const difference = dayjs.utc(postTime).diff(dayjs().utc());
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
    setTimeout(() => {
      setTimeLeft(calculateTimeLeft());
    }, 1000);
  });

  let timerComponents: JSX.Element[] = [];

  Object.keys(timeLeft).forEach((interval, i) => {
    if (!timeLeft[interval]) {
      return;
    }

    timerComponents.push(
      <span>
        {String(timeLeft[interval]).padStart(2, '0')}
        {i < Object.keys(timeLeft).length - 1 && ':'}
      </span>,
    );
  });

  return <>{timerComponents.length ? timerComponents : 'OFF'}</>;
}
