
import React, { useEffect, useState} from "react";
import eth from "../eth.png";
import dai from "../dai.png";
import rebel from "../rebel.png";
import { YourWallet } from './yourWallet';
import { DonkeyStakingContract } from './donkeyStakingContract';
import {useEthers} from '@usedapp/core';
import {constants} from "ethers"
import DonkeyToken from "../artifacts/contracts/DonkeyToken.json";

import { Snackbar, Typography, makeStyles} from "@material-ui/core";
import Alert from "@material-ui/lab/Alert";
import networkMapping from "../artifacts/deployments/map.json";
import brownieConfig from "../brownie_config.json";
import helperConfig from "../helper-config.json";



export type Token = {
    image: string
    address: string,
    name: string
}

const useStyles = makeStyles((theme) => ({
    title: {
        color: "#DAA520",
        boxShadow: "0px 0px 5px goldenrod",
        textAlign: "center",
        textDecoration: "underline",
        textShadow: "5px 5px 10px #0000F",
        fontFamily: "Inconsolata, monospace",
        padding: theme.spacing(4),
    }
}))

export const Main = () => {
    const {chainId, error} = useEthers();

    const classes = useStyles();
    const networkName = chainId ? helperConfig[chainId] : "dev";
    console.log(typeof chainId);

    const donkeyTokenAddress = chainId ? networkMapping[String(chainId)]["DonkeyToken"][0] : constants.AddressZero
    const wethTokenAddress = chainId ? brownieConfig["networks"][networkName]["weth_token"] : constants.AddressZero
    const fauTokenAddress = chainId ? brownieConfig["networks"][networkName]["fau_token"] : constants.AddressZero


    const supportedTokens: Array<Token> = [
        {
            image: eth,
            address: wethTokenAddress,
            name: "WETH",
        },
        {
            image: dai,
            address: fauTokenAddress,
            name: "DAI",
        },
        {
            image: rebel,
            address: donkeyTokenAddress,
            name: "Donkey"
        }
    ]

    const [showNetworkError, setShowNetworkError] = useState(false)

    const handleCloseNetworkError = (
        event: React.SyntheticEvent | React.MouseEvent,
        reason?: string
    ) => {
        if (reason === "clickaway") {
            return;
        }

        showNetworkError && setShowNetworkError(false);
    }

    useEffect(() => {
        if (error && error.name === "UnsupportedChainIdError") {
            !showNetworkError && setShowNetworkError(true)
        } else {
            showNetworkError && setShowNetworkError(false)
        }
    }, [error, showNetworkError])

    return (
    <>
    <Typography
        variant="h2"
        component="h1"
        classes={{
            root: classes.title
        }}
        >
           Donkey Token Staking
        </Typography>
        <YourWallet supportedTokens={supportedTokens} />
        <DonkeyStakingContract supportedTokens={supportedTokens} />
        <Snackbar
        open={showNetworkError}
        autoHideDuration={5000}
        onClose={handleCloseNetworkError}
    >
        <Alert onClose={handleCloseNetworkError} severity="warning">
        You must be connected to the Kovan network!
        </Alert>
    </Snackbar>
    </>
    )
}

