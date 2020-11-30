import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';

// The `withStyles()` higher-order component is injecting a `classes`
// prop that is used by the `Button` component.
const HinzuButton = withStyles({
  root: {
    background: '#633FAC',
    borderRadius: 3,
    border: 0,
    color: 'white',
    height: 48,
    padding: '0 30px',
    boxShadow: '0 3px 5px 2px rgba(255, 105, 135, .3)',
  },
  label: {
    textTransform: 'capitalize',
  },
})(Button);

export default HinzuButton;
