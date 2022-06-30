import React from 'react';
import { Form, Checkbox } from 'semantic-ui-react';
import { BET_LABELS } from './constants';

function BetTypeSelectForm({bets, betTypes, setBetTypes}) {
  const handleChange = (e, data) => {
    if (data.checked) {
      setBetTypes([...betTypes, data.name]);
    } else {
      setBetTypes(betTypes.filter(tc => tc !== data.name));
    }
  }


  return (
    <Form>
      <Form.Group grouped>
        {Object.keys(BET_LABELS).map(bt => (
          <Form.Field>
            <Checkbox name={bt} checked={betTypes.includes(bt)} label={BET_LABELS[bt]} onChange={handleChange} />
          </Form.Field>
        ))}
      </Form.Group>
    </Form>
  );
}

export default BetTypeSelectForm;
