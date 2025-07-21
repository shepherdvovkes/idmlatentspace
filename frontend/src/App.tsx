import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { store } from './store';
import Navbar from './components/layout/Navbar';
import Sidebar from './components/layout/Sidebar';
import Dashboard from './pages/Dashboard';
import Datasets from './pages/Datasets';
import Models from './pages/Models';
import Analysis from './pages/Analysis';
import Experiments from './pages/Experiments';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// IDM-themed dark theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00D4FF', // Cyan - Digital/Electronic
      dark: '#00A8CC',
      light: '#33DDFF',
    },
    secondary: {
      main: '#FF6B00', // Orange - Energy/Creativity
      dark: '#CC5500',
      light: '#FF8533',
    },
    background: {
      default: '#0A0A0A', // Deep Black
      paper: '#1A1A1A', // Dark Gray
    },
    surface: {
      main: '#2A2A2A', // Medium Gray
    },
    text: {
      primary: '#FFFFFF', // White
      secondary: '#B0B0B0', // Light Gray
    },
    success: {
      main: '#10B981', // Green
    },
    warning: {
      main: '#F59E0B', // Amber
    },
    error: {
      main: '#EF4444', // Red
    },
    info: {
      main: '#3B82F6', // Blue
    },
  },
  typography: {
    fontFamily: 'Inter, sans-serif',
    h1: {
      fontSize: '2rem',
      fontWeight: 600,
      color: '#FFFFFF',
    },
    h2: {
      fontSize: '1.75rem',
      fontWeight: 600,
      color: '#FFFFFF',
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 500,
      color: '#FFFFFF',
    },
    h4: {
      fontSize: '1.25rem',
      fontWeight: 500,
      color: '#FFFFFF',
    },
    h5: {
      fontSize: '1.125rem',
      fontWeight: 500,
      color: '#FFFFFF',
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
      color: '#FFFFFF',
    },
    body1: {
      fontSize: '1rem',
      color: '#B0B0B0',
    },
    body2: {
      fontSize: '0.875rem',
      color: '#B0B0B0',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          fontWeight: 500,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: '#1A1A1A',
          border: '1px solid #2A2A2A',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#1A1A1A',
          border: '1px solid #2A2A2A',
          borderRadius: 12,
        },
      },
    },
  },
});

// Augment the theme to include custom colors
declare module '@mui/material/styles' {
  interface Palette {
    surface: Palette['primary'];
  }

  interface PaletteOptions {
    surface?: PaletteOptions['primary'];
  }
}

function App() {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Box sx={{ display: 'flex', minHeight: '100vh' }}>
            {/* Navbar */}
            <Navbar onToggleSidebar={toggleSidebar} />
            
            {/* Sidebar */}
            <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
            
            {/* Main Content */}
            <Box
              component="main"
              sx={{
                flexGrow: 1,
                pt: '80px', // Account for navbar height
                pl: sidebarOpen ? '300px' : '60px', // Account for sidebar width
                transition: 'padding-left 0.3s ease',
                backgroundColor: 'background.default',
                minHeight: '100vh',
              }}
            >
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/datasets" element={<Datasets />} />
                <Route path="/models" element={<Models />} />
                <Route path="/analysis" element={<Analysis />} />
                <Route path="/experiments" element={<Experiments />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </Box>
          </Box>
          
          {/* Toast notifications */}
          <ToastContainer
            position="top-right"
            autoClose={5000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="dark"
          />
        </Router>
      </ThemeProvider>
    </Provider>
  );
}

export default App;