import React from 'react';
// Try the simple version first - fewer dependencies, guaranteed to work
import SimpleCommandCenter from '../../components/SimpleCommandCenter';

// If simple works, you can switch to enhanced later:
// import EnhancedUserCommandCenter from '../../components/EnhancedUserCommandCenter';
// import UserCommandCenter from '../../components/UserCommandCenter';

export const ControlCenterPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <SimpleCommandCenter />
    </div>
  );
};

export default ControlCenterPage;