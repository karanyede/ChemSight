import axios, {
  AxiosError,
  AxiosRequestConfig,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from "axios";
import { clearToken, getToken } from "../utils/auth";

type UnauthorizedCallback = () => void;

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
  headers: {
    "Content-Type": "application/json",
  },
});

let unauthorizedListeners: UnauthorizedCallback[] = [];

export const subscribeToUnauthorized = (
  callback: UnauthorizedCallback
): (() => void) => {
  unauthorizedListeners.push(callback);
  return () => {
    unauthorizedListeners = unauthorizedListeners.filter(
      (listener) => listener !== callback
    );
  };
};

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      clearToken();
      unauthorizedListeners.forEach((listener) => listener());
    }
    return Promise.reject(error);
  }
);

export interface DatasetSummary {
  total_records: number;
  average_flowrate: number;
  average_pressure: number;
  average_temperature: number;
  type_distribution: Record<string, number>;
}

export const login = async (username: string, password: string) => {
  const { data } = await api.post("auth/login/", { username, password });
  return data as { token: string };
};

export const register = async (
  username: string,
  password: string,
  email?: string
) => {
  const payload = { username, password, email };
  const { data } = await api.post("auth/register/", payload);
  return data as { token: string };
};

export const uploadDataset = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post("upload/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
};

export const getDatasets = async (params?: Record<string, string | number>) => {
  const { data } = await api.get("datasets/", { params });
  return data;
};

export const getDataset = async (id: number) => {
  const { data } = await api.get(`datasets/${id}/`);
  return data;
};

export const getDatasetSummary = async (id: number) => {
  const { data } = await api.get(`datasets/${id}/summary/`);
  return data as DatasetSummary;
};

export const getDatasetRecords = async (
  id: number,
  params?: Record<string, string | number>
) => {
  const { data } = await api.get(`datasets/${id}/records/`, { params });
  return data;
};

export const downloadReport = async (id: number) => {
  const response = await api.get(`datasets/${id}/report/`, {
    responseType: "blob",
  });
  return response.data as Blob;
};

export const getMetrics = async () => {
  const { data } = await api.get("metrics/");
  return data;
};

export default api;
