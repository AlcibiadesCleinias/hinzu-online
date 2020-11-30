import React from "react";
import {
  Link
} from "react-router-dom";
import UploadService from "../../services/FileUploadService";
// material ui
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import CardMedia from '@material-ui/core/CardMedia';
import Grid from '@material-ui/core/Grid';
import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import ThumbUpIcon from '@material-ui/icons/ThumbUp';
import ShareIcon from '@material-ui/icons/Share';
import IconButton from '@material-ui/core/IconButton';
import ThumbDownIcon from '@material-ui/icons/ThumbDown';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';

import TelegramIcon from '@material-ui/icons/Telegram';
import GetAppIcon from '@material-ui/icons/GetApp';
import WhatsAppIcon from '@material-ui/icons/WhatsApp';

const useStyles = makeStyles((theme) => ({
  heroContent: {
    backgroundColor: theme.palette.background.paper,
    padding: theme.spacing(0, 0, 6),
    "color": '#633FAC',
  },
  underCardGrid: {
    paddingTop: theme.spacing(3),
    paddingBottom: theme.spacing(3),
  },
  card: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
  },
  cardImgOnly: {
    // height: '100%',
    display: 'flex',
    flexDirection: 'column',
    padding: 0,
    "&:last-child": {
      paddingBottom: 0,
    }
  },
  cardMedia: {
    paddingTop: '56.25%', // 16:9
  },
  cardContent: {
    flexGrow: 1,
  },
}));

const ResultView = (props) => {
  const classes = useStyles();
  const url = props.url;
  const film = props.film;
  const imageCrypted = props.imageCrypted;
  const url4search = props.url4search;

  const [anchorEl, setAnchorEl] = React.useState(null);
  const [colorUpIcon, setColorUpIcon] = React.useState(null);
  const [colorDownIcon, setColorDownIcon] = React.useState(null);
  const [progress, setProgress] = React.useState(0);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const vote = (user_rate) => {
    UploadService.userVote(user_rate, (event) => {
      setProgress(Math.round((100 * event.loaded) / event.total));
    })
      .then((response) => {
        return null
      })
      .catch(() => {
        setProgress(0);
      });
  };

  const handleClickUpIcon = () => {
    if (colorUpIcon == null) {
      setColorUpIcon('green');
      setColorDownIcon(null);
      vote(1);
    } else {
      setColorUpIcon(null);
      setColorDownIcon(null);
      vote(null);
    }
  };

  const handleClickDownIcon = () => {
    if (colorDownIcon == null) {
      setColorDownIcon('red');
      setColorUpIcon(null);
      vote(0);
    } else {
      setColorDownIcon(null);
      setColorUpIcon(null);
      vote(null);
    }
  };

  return (
    <Grid container spacing={2} justify="center">
      <Grid xs={12} sm={7} md={7} item>
        <Card className={classes.card}>
          <CardMedia
            className={classes.cardImgOnly}
            >
            <Link
              to={{pathname: url}}
              target='_blank'
                >
              <img
                src={url}
                style={{width: '100%'}}
              />
            </Link>
          </CardMedia>
          <CardContent>
            <Typography variant="subtitle1" color="textSecondary" component="p" align='center'>
              Хм-м... из какого же это фильма?
            </Typography>
            <Typography variant="body2" style={{color:"#633FAC"}} component="p" align='center'>
              Hinzu говорит, это из «
              <Link
                to={{ pathname: "http://www.google.com/search?q=film+" + url4search }}
                target="_blank"
                style={{ color: '#633FAC', textDecoration: 'none' }}
                >
                {film}
              </Link>
              »
            </Typography>
          </CardContent>
          <CardActions disableSpacing>
            <IconButton
              aria-label="poshadi"
              style={{color:colorUpIcon}}
              onClick={handleClickUpIcon}
              >
              <ThumbUpIcon />
            </IconButton>
            <IconButton
              aria-label="kill him"
              style={{color:colorDownIcon}}
              onClick={handleClickDownIcon}
              >
              <ThumbDownIcon />
            </IconButton>
            <IconButton
              style={{marginLeft: 'auto',}}
              aria-label="show more"
              aria-controls="simple-menu"
              aria-haspopup="true"
              onClick={handleClick}
            >
              <ShareIcon />
            </IconButton>
            <Menu
              id="simple-menu"
              anchorEl={anchorEl}
              keepMounted
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
            <Link
              to={{ pathname: url }}
              target="_blank"
              style={{ color: '#696969', textDecoration: 'none' }}
              >
              <MenuItem onClick={handleClose}><GetAppIcon/> Скачать</MenuItem>
            </Link>
            <Link
              to={{ pathname: "https://telegram.me/share/url?url=https%3A%2F%2Fhinzu.online%2Fhinzu-django%2Fapi%2Ffetch-image%2F" + imageCrypted +"&text=Hinzu%2C%20Make%20the%20Magic&utm_source=share2" }}
              target="_blank"
              style={{ color: '#696969', textDecoration: 'none' }}
              >
                <MenuItem onClick={handleClose}><TelegramIcon/> Telegram</MenuItem>
            </Link>
            <Link
              to={{ pathname: "https://api.whatsapp.com/send?text=Hinzu%2C%20Make%20the%20Magic%20https%3A%2F%2Fhinzu.online%2Fhinzu-django%2Fapi%2Ffetch-image%2F" + imageCrypted + "&utm_source=share2" }}
              target="_blank"
              style={{ color: '#696969', textDecoration: 'none' }}
              >
                <MenuItem onClick={handleClose}><WhatsAppIcon/> WhatsApp</MenuItem>
            </Link>
            </Menu>
          </CardActions>
        </Card>
      </Grid>

      <Grid container spacing={2} className={classes.underCardGrid}>
      </Grid>

    </Grid>
  );
};

export default ResultView;
