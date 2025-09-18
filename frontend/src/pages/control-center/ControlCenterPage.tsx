import React from 'react';
import UserCommandCenter from '../../components/UserCommandCenter';

export const ControlCenterPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <UserCommandCenter defaultTab="command" />
    </div>
  );
};

export default ControlCenterPage;