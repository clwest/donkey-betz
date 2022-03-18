import React, {useState} from "react";
import {useEthers} from "@usedapp/core";
import { TabContext, TabList, TabPanel} from "@material-ui/lab"
import {
    ConnectionRequireMsg,
} from "../../helpers";
import {Tab, Box, makeStyles} from "@material-ui/core";
import {Token} from "../Main";
import {Unstake} from "./Unstake";

interface DonkeyStakingContactProps {
    supportedTokens: Array<Token>;
}

const useStyles = makeStyles((theme) => ({
    tabContent: {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: theme.spacing(4),
    },
    box: {
        backgroundColor: "#F09C22",
        borderRadius: "40px",
        boxShadow: "0 9px #9B300A",
        margin: `${theme.spacing(4)}px 0`,
        padding: theme.spacing(2),
    },
    header: {
      color: "#DAA520",
      textShadow: "2px 2px 5px #DC143C"
    }
}))


export const DonkeyStakingContract = ({
    supportedTokens,
}: DonkeyStakingContactProps) => {
    const classes = useStyles();
    const [selectedTokenIndex, setSelectedTokenIndex] = useState<number>(0);

    const handleChange = (event: React.ChangeEvent<{}>, newValue: string) => {
        setSelectedTokenIndex(parseInt(newValue));
    }
    
    const {account} = useEthers();
    const isConnected = account !== undefined

    return (
        <Box>
          <h1 className={classes.header}>Donkey Yield Earnings</h1>
          <Box className={classes.box}>
            <div>
              {isConnected ? (
                <TabContext value={selectedTokenIndex.toString()}>
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
                        <Unstake token={token} />
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