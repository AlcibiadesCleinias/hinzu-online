import React from "react";
// import components
import HinzuFooter from '../../components/Footer';
import HinzuExample from './Components/Examples';
import HinzuUpload from './Components/ImageUploadAction';
import HinzuHeader from '../../components/Header';

// material ui
import CssBaseline from '@material-ui/core/CssBaseline';

const UploadFiles = () => {
  return (
    <div>
      <CssBaseline/>
      <HinzuHeader/>
      <HinzuUpload/>
      <HinzuExample/>
      <HinzuFooter/>
    </div>
  );
};

export default UploadFiles;
