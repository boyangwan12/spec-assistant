import axios from "axios";

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return axios.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const parseFile = (filename) => axios.post("/parse", { filename });
export const chunkFile = (filename) => axios.post("/chunk", { filename });
export const embedFile = (filename) => axios.post("/embed", { filename });
export const chatWithDoc = (query, filename) => axios.post("/chat", { query, filename });
