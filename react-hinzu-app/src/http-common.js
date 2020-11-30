import axios from "axios";

export default axios.create({
  baseURL: "https://hinzu.online/hinzu-django/api-react",
  headers: {
    "Content-type": "application/json"
  },
  withCredentials: true,
});
