import React, { useState, useEffect } from 'react';
import dayjs from 'dayjs';
import {Label} from 'semantic-ui-react';
var utc = require('dayjs/plugin/utc');
dayjs.extend(utc);

function PostTimer({postTime}) {
  const calculateTimeLeft = () => {
    const difference = dayjs.utc(postTime) - dayjs().utc();
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

  const timerComponents = [];

  Object.keys(timeLeft).forEach((interval, i) => {
    if (!timeLeft[interval]) {
      return;
    }

    timerComponents.push(
      <span>
        {String(timeLeft[interval]).padStart(2, '0')}{i < Object.keys(timeLeft).length - 1 && ':'}
      </span>
    )
  });

  return (
    <Label horizontal>
      {timerComponents.length ? timerComponents : 'OFF'}
    </Label>
  );
}

export default PostTimer;
