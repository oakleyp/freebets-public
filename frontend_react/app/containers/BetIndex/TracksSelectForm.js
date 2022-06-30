import React from 'react';
import { Form, Checkbox } from 'semantic-ui-react';
import PropTypes from 'prop-types';
import { ALL_TRACKS } from './constants';

function TracksSelectForm({enabledTrackCodes, setTrackCodes}) {
  const handleChange = (e, data) => {
    if (data.checked) {
      setTrackCodes([...enabledTrackCodes, data.name]);
    } else {
      setTrackCodes(enabledTrackCodes.filter(tc => tc !== data.name));
    }
  }

  return (
    <Form>
      <Form.Group grouped>
        {ALL_TRACKS.map(tc => (
          <Form.Field>
            <Checkbox label={tc.toUpperCase()} name={tc} checked={enabledTrackCodes.includes(tc)} onChange={handleChange} />
          </Form.Field>
        ))}
      </Form.Group>
    </Form>
  );
}

TracksSelectForm.propTypes = {
  bets: PropTypes.object,
  trackCodes: PropTypes.arrayOf(PropTypes.string),
  setTrackCodes: PropTypes.func,
}

TracksSelectForm.defaultProps = {
  bets: {
    single_bets: [],
    multi_bets: [],
  },
  trackCodes: [],
}

export default TracksSelectForm;
