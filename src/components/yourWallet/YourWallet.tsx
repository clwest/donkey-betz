import React, {useState } from 'react';
import {useEthers} from "@usedapp/core";
import {StakeForm} from "./StakeForm";
import { Tab, makeStyles, Box} from "@material-ui/core";
import { TabContext, TabList, TabPanel} from "@material-ui/lab";
import {
    ConnectionRequireMsg
} from "../../helpers";
import { Token } from "../Main"
import { WalletBalance } from "./WalletBalance";

interface YourWalletProps {
    supportedTokens: Array<Token>
}

const useStyles = makeStyles((theme) => ({
    tabContent: {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: theme.spacing(4),
    },
    box: {
        backgroundColor: "white",
        borderRadius: "25px",
    },
    header: {
        color: "white",
    }
}))
export const YourWallet = ({ supportedTokens }: YourWalletProps) => {
    const [ selectedTokensIndex, setSelectedTokensIndex] = useState<number>(0);

    const handleChange = (event: React.ChangeEvent<{}>, newValue: string) => {
        setSelectedTokensIndex(parseInt(newValue));
    }

    const { account } = useEthers();
    const isConnected = account !== undefined;

    const classes = useStyles();


    return (
        <Box>
        <h1 className={classes.header}>Your Wallet</h1>
          <Box className={classes.box}>
            <div>
              {isConnected ? (
                <TabContext value={selectedTokensIndex.toString()}>
                  <TabList onChange={handleChange} aria-label="stake form tabs">
                    {supportedTokens.map((token, index) => {
                      return (
                        <Tab
                          label={token.name}
                          value={index.toString()}
                          key={index}
                        />
                      )
                    })}
                  </TabList>
                  {supportedTokens.map((token, index) => {
                    return (
                      <TabPanel value={index.toString()} key={index}>
                        <div className={classes.tabContent}>
                          <WalletBalance
                            token={supportedTokens[selectedTokensIndex]}
                          />
                          {/* this is the same as */}
                          {/* The chainlink_defi props passing */}
                          <StakeForm token={supportedTokens[selectedTokensIndex]} />
                        </div>
                      </TabPanel>
                    )
                  })}
                </TabContext>
              ) : (
                <ConnectionRequireMsg />
              )}
            </div>
          </Box>
        </Box>
      )


}