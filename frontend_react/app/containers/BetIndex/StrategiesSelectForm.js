import React from 'react';
import { Form, Checkbox } from 'semantic-ui-react';
import { ALL_STRATS } from './constants';

function StrategiesSelectForm({bets, strategies, setStrategies}) {
  const handleChange = (e, data) => {
    if (data.checked) {
      setStrategies([...strategies, data.name]);
    } else {
      setStrategies(strategies.filter(tc => tc !== data.name));
    }
  }

  return (
    <Form>
      <Form.Group grouped>
        {ALL_STRATS.map(strat => (
          <Form.Field>
            <Checkbox label={strat} name={strat} onChange={handleChange} checked={strategies.includes(strat)} />
          </Form.Field>
        ))}
      </Form.Group>
    </Form>
  );
}

export default StrategiesSelectForm;
