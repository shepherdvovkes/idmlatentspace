import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

export interface Dataset {
  id: string;
  name: string;
  description?: string;
  fileCount: number;
  totalPresets: number;
  qualityScore?: number;
  status: 'uploading' | 'processing' | 'ready' | 'error';
  createdAt: string;
  updatedAt?: string;
}

export interface PreprocessingJob {
  id: string;
  datasetId: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress: number;
  config: any;
  error?: string;
}

interface DatasetState {
  datasets: Dataset[];
  currentDataset: Dataset | null;
  preprocessingJobs: PreprocessingJob[];
  loading: boolean;
  error: string | null;
}

const initialState: DatasetState = {
  datasets: [],
  currentDataset: null,
  preprocessingJobs: [],
  loading: false,
  error: null,
};

// Async thunks
export const fetchDatasets = createAsyncThunk(
  'datasets/fetchDatasets',
  async () => {
    const response = await fetch('/api/v1/datasets');
    return response.json();
  }
);

export const uploadDataset = createAsyncThunk(
  'datasets/uploadDataset',
  async (formData: FormData) => {
    const response = await fetch('/api/v1/datasets', {
      method: 'POST',
      body: formData,
    });
    return response.json();
  }
);

export const startPreprocessing = createAsyncThunk(
  'datasets/startPreprocessing',
  async ({ datasetId, config }: { datasetId: string; config: any }) => {
    const response = await fetch(`/api/v1/datasets/${datasetId}/preprocess`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });
    return response.json();
  }
);

const datasetSlice = createSlice({
  name: 'datasets',
  initialState,
  reducers: {
    setCurrentDataset: (state, action: PayloadAction<Dataset | null>) => {
      state.currentDataset = action.payload;
    },
    updatePreprocessingJob: (state, action: PayloadAction<PreprocessingJob>) => {
      const index = state.preprocessingJobs.findIndex(job => job.id === action.payload.id);
      if (index !== -1) {
        state.preprocessingJobs[index] = action.payload;
      } else {
        state.preprocessingJobs.push(action.payload);
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch datasets
      .addCase(fetchDatasets.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDatasets.fulfilled, (state, action) => {
        state.loading = false;
        state.datasets = action.payload;
      })
      .addCase(fetchDatasets.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch datasets';
      })
      // Upload dataset
      .addCase(uploadDataset.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(uploadDataset.fulfilled, (state, action) => {
        state.loading = false;
        state.datasets.push(action.payload);
      })
      .addCase(uploadDataset.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to upload dataset';
      })
      // Start preprocessing
      .addCase(startPreprocessing.fulfilled, (state, action) => {
        state.preprocessingJobs.push(action.payload);
      });
  },
});

export const { setCurrentDataset, updatePreprocessingJob, clearError } = datasetSlice.actions;
export default datasetSlice.reducer;