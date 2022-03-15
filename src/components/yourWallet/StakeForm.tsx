
import React, { useEffect, useState } from 'react';
import { SliderInput } from "../../helpers";
import { useEthers, useTokenBalance, useNotifications } from '@usedapp/core';
import {formatUnits} from "@ethersproject/units";
import {
    Button,
    CircularProgress,
    Snackbar,
    makeStyles,
} from '@material-ui/core';
import {Token} from "../Main";
import { useStakeTokens } from "../../hooks"
import {utils} from "ethers";
import Alert from "@material-ui/lab/Alert";
import "../../App.css";



export interface StakeFormProps {
    token: Token;
}


const useStyles = makeStyles((theme) => ({
    container: {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: theme.spacing(2),
        width: "50%",
    },
    slider: {
        width: "100%",
        maxWidth: "400px",
    },

}));


export const StakeForm = ({token}: StakeFormProps) => {
    const {address: tokenAddress, name} = token;

    const { account } = useEthers();
    const tokenBalance = useTokenBalance(tokenAddress, account);
    const { notifications } = useNotifications();

    const classes = useStyles();

    const { send: stakeTokensSend, state: stakeTokensState} = useStakeTokens(tokenAddress)

    const formattedTokenBalance: number = tokenBalance ? parseFloat(formatUnits(tokenBalance, 18)) : 0;

    const handleStakeSubmit = () => {
        const amountAsWei = utils.parseEther(amount.toString())
        return stakeTokensSend(amountAsWei.toString())
    }

    const [amount, setAmount] =
    useState<number | string | Array<number | string>>(0);
    
    const [showDonkeyTokenApprovalSuccess, setShowDonkeyTokenApprovalSuccess] =
        useState(false)
    const [showStakeTokensSuccess, setShowStakeTokensSuccess] = useState(false)
    
    const handleCloseSnack = () => {
        showDonkeyTokenApprovalSuccess && setShowDonkeyTokenApprovalSuccess(false)
        showStakeTokensSuccess && setShowStakeTokensSuccess(false)
    }

    useEffect(() => {
        if ( notifications.filter(
        (notification) =>
            notification.type === "transactionSucceed" &&
            notification.transactionName === "Approve Donkey Token transfer"
        ).length > 0
        ) {
            setShowDonkeyTokenApprovalSuccess && setShowDonkeyTokenApprovalSuccess(false)
            !showStakeTokensSuccess && setShowStakeTokensSuccess(true)
            
        }
    }, [notifications, showDonkeyTokenApprovalSuccess, showStakeTokensSuccess]) 

    const isMining = stakeTokensState.status === "Mining"

    const hasZeroBalance = formattedTokenBalance === 0
    const hasZeroAmountStaked = parseFloat(amount.toString()) === 0

    return (
        <>
        <div className={classes.container}>
            <SliderInput
                label={`Stake ${name}`}
                maxValue={formattedTokenBalance}
                id={`slider-input-${name}`}
                className={classes.slider}
                value={amount}
                onChange={setAmount}
                disabled={isMining || hasZeroBalance}

            />
            <Button
                color="primary"
                variant="contained"
                size="large"
                onClick={handleStakeSubmit}
                disabled={isMining || hasZeroBalance}
            >
                {isMining ? <CircularProgress size={26} /> : "Stake"}
            </Button>
            </div>
            <Snackbar
                open={showDonkeyTokenApprovalSuccess}
                autoHideDuration={5000}
                onClose={handleCloseSnack}
            >
                <Alert onClose={handleCloseSnack} severity="success">
                    Token transfer approved successfully! Now approve the second transaction to initiate the staking transfer.
                </Alert>
            </Snackbar>
            <Snackbar
                open={showStakeTokensSuccess}
                autoHideDuration={5000}
                onClose={handleCloseSnack}
            >
                <Alert onClose={handleCloseSnack} severity="success">
                    Tokens staked successfully!
                </Alert>
            </Snackbar>
        </>
    )

}