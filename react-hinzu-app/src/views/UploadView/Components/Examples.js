import React from "react";
// material ui
import Card from '@material-ui/core/Card';
import CardMedia from '@material-ui/core/CardMedia';
import Grid from '@material-ui/core/Grid';
import { makeStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';

import Image1 from "../../../assets/images/1.jpg";
import Image2 from "../../../assets/images/2.jpg";
import Image3 from "../../../assets/images/3.jpg";
import Image4 from "../../../assets/images/4.jpg";

const Imagelist = [Image1, Image2, Image3, Image4]

const useStyles = makeStyles((theme) => ({
  cardGrid: {
    paddingTop: theme.spacing(8),
    paddingBottom: theme.spacing(8),
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
const cards = [1, 2, 3, 4];

const Examples = () => {
  const classes = useStyles();
  return (
   <Container className={classes.cardGrid} maxWidth="md">
     {/* End hero unit */}
     <Grid container spacing={4}>
       {cards.map((card) => (
         <Grid item key={card} xs={12} sm={6} md={3}>
           <Card
             className={classes.cardImgOnly}>
           <CardMedia
             className={classes.cardImgOnly}
             >
             <img
               src={Imagelist[card-1]}
               style={{width: '100%'}}
               alt='Лучшие работы Hinzu'
             />
           </CardMedia>
           </Card>
         </Grid>
       ))}
     </Grid>
   </Container>

  );
};

export default Examples;
