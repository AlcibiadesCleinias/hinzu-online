// services for post and get data

import http from "../http-common";

const upload = (file, onUploadProgress) => {
  let formData = new FormData();

  formData.append('file', file, file.name);

  return http.post("/upload/", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress,
  });
};

const getFiles = () => {
  return http.get("/posts");
};

const userVote = (rate, onUploadProgress) => {
  let formData = new FormData();
  formData.append('rateNone', rate);
  formData.append('rate', rate);
  console.log(formData);

  return http.post('/addlike/', formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress,
  })
};

export default {
  upload,
  getFiles,
  userVote,
};
