import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface MLModel {
  id: string;
  name: string;
  algorithm: string;
  status: 'training' | 'completed' | 'failed';
  accuracy: number;
  createdAt: string;
}

interface ModelState {
  models: MLModel[];
  currentModel: MLModel | null;
  loading: boolean;
  error: string | null;
}

const initialState: ModelState = {
  models: [],
  currentModel: null,
  loading: false,
  error: null,
};

const modelSlice = createSlice({
  name: 'models',
  initialState,
  reducers: {
    setModels: (state, action: PayloadAction<MLModel[]>) => {
      state.models = action.payload;
    },
    addModel: (state, action: PayloadAction<MLModel>) => {
      state.models.push(action.payload);
    },
    updateModel: (state, action: PayloadAction<MLModel>) => {
      const index = state.models.findIndex(m => m.id === action.payload.id);
      if (index !== -1) {
        state.models[index] = action.payload;
      }
    },
    setCurrentModel: (state, action: PayloadAction<MLModel | null>) => {
      state.currentModel = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const {
  setModels,
  addModel,
  updateModel,
  setCurrentModel,
  setLoading,
  setError,
} = modelSlice.actions;

export default modelSlice.reducer;