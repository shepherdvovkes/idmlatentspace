import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AnalysisResult {
  id: string;
  presetName: string;
  genrePredictions: Record<string, number>;
  similarPresets: Array<{
    id: string;
    name: string;
    similarity: number;
  }>;
  featureImportance: Record<string, number>;
  timestamp: string;
}

interface AnalysisState {
  results: AnalysisResult[];
  currentResult: AnalysisResult | null;
  isAnalyzing: boolean;
  error: string | null;
}

const initialState: AnalysisState = {
  results: [],
  currentResult: null,
  isAnalyzing: false,
  error: null,
};

const analysisSlice = createSlice({
  name: 'analysis',
  initialState,
  reducers: {
    setResults: (state, action: PayloadAction<AnalysisResult[]>) => {
      state.results = action.payload;
    },
    addResult: (state, action: PayloadAction<AnalysisResult>) => {
      state.results.unshift(action.payload);
    },
    setCurrentResult: (state, action: PayloadAction<AnalysisResult | null>) => {
      state.currentResult = action.payload;
    },
    setAnalyzing: (state, action: PayloadAction<boolean>) => {
      state.isAnalyzing = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    clearResults: (state) => {
      state.results = [];
      state.currentResult = null;
    },
  },
});

export const {
  setResults,
  addResult,
  setCurrentResult,
  setAnalyzing,
  setError,
  clearResults,
} = analysisSlice.actions;

export default analysisSlice.reducer;