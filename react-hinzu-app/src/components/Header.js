import React from "react";
// material ui
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';

const useStyles = makeStyles((theme) => ({
  heroContent: {
    backgroundColor: theme.palette.background.paper,
    padding: theme.spacing(8, 0, 1),
    "color": '#633FAC',
  },
}));

const Header = () => {
  const classes = useStyles();
  return (
   <div className={classes.heroContent}>
     <Container maxWidth="sm">
       <Typography component="h1" variant="h3" align="center" gutterBottom style={{ fontFamily: 'Girloub' }}>
         Из какого ты фильма?
       </Typography>
       <Typography variant="body1" align="center" color="textSecondary" paragraph>
         Загружай свои фото в разных ситуациях
       </Typography>
     </Container>
   </div>
  );
};

export default Header;
