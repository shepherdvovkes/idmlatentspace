import { configureStore } from '@reduxjs/toolkit';
import datasetReducer from './slices/datasetSlice';
import modelReducer from './slices/modelSlice';
import analysisReducer from './slices/analysisSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    datasets: datasetReducer,
    models: modelReducer,
    analysis: analysisReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;