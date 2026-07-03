import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import DogFood from './pages/DogFood';
import DogTreats from './pages/DogTreats';
import Seasonality from './pages/Seasonality';
import Influencers from './pages/Influencers';
import Logistics from './pages/Logistics';
import PainPoints from './pages/PainPoints';
import Methodology from './pages/Methodology';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dog-food" element={<DogFood />} />
        <Route path="/dog-treats" element={<DogTreats />} />
        <Route path="/toilets" element={<Navigate to="/dog-food" replace />} />
        <Route path="/toilet-seats" element={<Navigate to="/dog-treats" replace />} />
        <Route path="/bathtubs" element={<Navigate to="/dog-food" replace />} />
        <Route path="/insights/seasonality" element={<Seasonality />} />
        <Route path="/insights/influencers" element={<Influencers />} />
        <Route path="/insights/painpoints" element={<PainPoints />} />
        <Route path="/insights/logistics" element={<Logistics />} />
        <Route path="/methodology" element={<Methodology />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
