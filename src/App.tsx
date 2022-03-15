import React from 'react';
import { DAppProvider, ChainId } from '@usedapp/core';
import { Header } from "./components/Header";
import { Main } from './components/Main'
import { Container } from "@material-ui/core";



function App() {
  return (

    <DAppProvider config={{
      supportedChains: [ChainId.Kovan, ChainId.Rinkeby],
      notifications: {
        expirationPeriod: 1000,
        checkInterval: 1000
      }
    }}>
      <Header />
      <Container maxWidth="md">
      <Main />
      </Container>  
    </DAppProvider>
  );
}

export default App;
