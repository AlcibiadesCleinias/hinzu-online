import React from "react";

// material ui
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import Link from '@material-ui/core/Link';

function Copyright() {
  return (
    <Typography variant="body2" color="textSecondary" align="center">
      {'Copyright © '}
      <Link color="inherit" href="https://hinzu.online/hinzu-django/">
        hinzu.online
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}

const useStyles = makeStyles((theme) => ({
  footer: {
    backgroundColor: theme.palette.background.paper,
    "color": '#633FAC',
    padding: theme.spacing(6),
  },
}));

const Footer = () => {
  const classes = useStyles();
  return (
   <footer className={classes.footer}>
     <Typography variant="h2" align="center" style={{fontFamily: 'Girloub'}} gutterBottom>
       HINZU
     </Typography>
     <Typography variant="subtitle1" align="center" color="textSecondary" component="p">
       <Link
        href="mailto:kadochnikova@bk.ru?subject=Вопрос по Hinzu.online"
        color="inherit"
        >
         kadochnikova@bk.ru
       </Link>
     </Typography>
     <Copyright />
   </footer>

  );
};

export default Footer;
