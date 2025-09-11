import React from 'react';
// Import the SportsBoardPage which has real sports data
import { SportsBoardPage } from '../../features/sports/pages/SportsBoardPage';

export const BettingPage: React.FC = () => {
  console.log('[BettingPage] Component rendering with SportsBoardPage...');
  
  return <SportsBoardPage />;
};