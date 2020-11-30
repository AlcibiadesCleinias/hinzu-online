import React, { useState } from "react";
import UploadService from "../../../services/FileUploadService";
// import components
import HinzuButton from '../../../components/HinzuButton';
import ResultView from '../../ResultView/ResultView';
// material ui
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardMedia from '@material-ui/core/CardMedia';
import Grid from '@material-ui/core/Grid';
import { makeStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import Skeleton from '@material-ui/lab/Skeleton';

import Alert from '@material-ui/lab/Alert';
import IconButton from '@material-ui/core/IconButton';
import Collapse from '@material-ui/core/Collapse';
import CloseIcon from '@material-ui/icons/Close';

const useStyles = makeStyles((theme) => ({
  // icon: {
  //   marginRight: theme.spacing(2),
  // },
  heroContent: {
    backgroundColor: theme.palette.background.paper,
    padding: theme.spacing(0, 0, 6),
    "color": '#633FAC',
  },
  // heroButtons: {
  //   marginTop: theme.spacing(4),
  // },
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
  mediaSkelet: {
    height: 390,
},
}));

const ImageUploadAction = () => {
  const classes = useStyles();

  const [selectedFiles, setSelectedFiles] = useState(undefined);
  const [currentFile, setCurrentFile] = useState(undefined);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("error");

  const [imagePreviewUrl, setImagePreviewUrl] = useState('');
  const [ifmessage, setIfmessage] = useState(false);

  const [uploadStart, setUploadStart] = useState(false);
  const [resultUrl, setResultUrl] = useState('');
  const [resultUrl4Search, setResultUrl4Search] = useState('');
  const [resultImageCrypted, setResultImageCrypted] = useState('');
  const [resultFilm, setResultFilm] = useState('');

  const selectFile = (event) => {
  setIfmessage(false);
  setUploadStart(false);
  setResultUrl('');
  setSelectedFiles(event.target.files);

  let reader = new FileReader();
  let file = event.target.files[0];

  reader.onloadend = () => {
    setImagePreviewUrl(reader.result);
  }
  reader.readAsDataURL(file)
  };

  const upload = () => {
    setImagePreviewUrl(false);
    setUploadStart(true);
    let currentFile = selectedFiles[0];

    setProgress(0);
    setCurrentFile(currentFile);

    UploadService.upload(currentFile, (event) => {
      // console.log(event);
      setProgress(Math.round((100 * event.loaded) / event.total));
    })
      .then((response) => {
        setMessage(response.data.message);
        setIfmessage(true);
        setMessageType('success');
        setResultUrl('https://hinzu.online/hinzu-django/api/fetch-image/' + response.data.path2combined_crypted);
        setResultImageCrypted(response.data.path2combined_crypted);
        setResultFilm(response.data.movie_name);
        setResultUrl4Search(response.data.movie_name_4search);
        // return UploadService.getFiles();
      })
      // .then((files) => {
      //   setFileInfos(files.data);
      //   setMessage("Uploaded successfully");
      // })
      .catch(() => {
        setProgress(0);
        setCurrentFile(undefined);
        setImagePreviewUrl(true);

        setMessage("Oops, похоже, какая-то ошибка на стороне сервера ;(");
        setIfmessage(true);
        setMessageType('error');
      });

    setSelectedFiles(undefined);
  };

  const cancel = () => {
    setSelectedFiles(undefined);
    setImagePreviewUrl('');
    setUploadStart(false);
    setIfmessage(false);
  };

  // if (progress === 100) {return <Redirect to="/result" />}

  let $imagePreview = null;
   if (imagePreviewUrl) {
     $imagePreview = (
   <Grid container spacing={2} justify="center">
     <Grid xs={12} sm={6} md={6} item>
       <Card className={classes.card}>
         <CardMedia
           className={classes.cardImgOnly}
           >
           <img
             src={imagePreviewUrl}
             style={{width: '100%'}}
           />
         </CardMedia>
       </Card>
     </Grid>

     <Grid container spacing={2} justify="center" className={classes.underCardGrid}>
       {selectedFiles ? (
         <Grid item>
           <HinzuButton
             variant="contained"
             color="primary"
             onClick={upload}
             >
             Найти фильм
           </HinzuButton>
         </Grid>
       ) : (<div></div>)}
       <Grid item>
         <HinzuButton
           variant="contained"
           color="primary"
           onClick={cancel}
           >
           Отмена
         </HinzuButton>
       </Grid>
    </Grid>
   </Grid>
     );
   } else {
     $imagePreview = (<div></div>);
   }

  return (
<div>
   <div className={classes.heroContent}>
     <Container maxWidth="sm">

       <Collapse in={ifmessage}>
          <Alert
            severity={messageType}
            variant="filled"
            action={
              <IconButton
                aria-label="close"
                color="inherit"
                size="small"
                onClick={() => {
                  setMessage("");
                  setIfmessage(false);
                }}
              >
                <CloseIcon fontSize="inherit" />
              </IconButton>
            }
          >
            {message}
          </Alert>
        </Collapse>

        <br/>

        {uploadStart ? ((resultUrl) ? (
          <ResultView
          url={resultUrl}
          imageCrypted={resultImageCrypted}
          film={resultFilm}
          url4search={resultUrl4Search}/>
        ) : (
          <Grid container spacing={2} justify="center">
            <Grid xs={12} sm={7} md={7} item>
              <Card className={classes.card}>
                <CardMedia
                  className={classes.cardImgOnly}
                  >
                 <Skeleton animation="wave" variant="rect" className={classes.mediaSkelet} />
               </CardMedia>
               <CardContent>

                <Skeleton animation="wave" height={10} style={{ marginBottom: 6 }} />
                <Skeleton animation="wave" height={10} width="100%" />
               </CardContent>
             </Card>
           </Grid>
           <Grid container spacing={2} className={classes.underCardGrid}>
           </Grid>
         </Grid>
        )) : (null)}

       {!imagePreviewUrl ? (
         <div>
           <Grid container spacing={2} justify="center">
             <Grid item>
               <input
               accept="image/*"
               className={classes.input}
               id="raised-button-file"
               // multiple
               type="file"
               style={{ display: 'none' }}
               onChange={selectFile}
               />
               <label htmlFor="raised-button-file">
                 <HinzuButton component="span" variant="contained" color="primary">
                   Выбрать фото
                 </HinzuButton>
               </label>
             </Grid>
           </Grid>
         </div>
       ) : (
         <div>
           {$imagePreview}
         </div>
       )}

     </Container>
   </div>
</div>

  );
};

export default ImageUploadAction;
