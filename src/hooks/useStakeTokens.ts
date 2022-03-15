import { useEffect, useState} from 'react'
import {useContractFunction, useEthers } from '@usedapp/core'
import DonkeyStaking from '../artifacts/contracts/DonkeyStaking.json'
import DonkeyToken from '../artifacts/contracts/DonkeyToken.json'
import { utils, constants} from "ethers"
import { Contract } from "@ethersproject/contracts"
import networkMapping from "../artifacts/deployments/map.json"

export const useStakeTokens = (donkeyTokenAddress: string) => {
    const { chainId } = useEthers();
    const { abi } = DonkeyStaking;


    const donkeyStakingContractAddress = chainId ? networkMapping[String(chainId)]["DonkeyStaking"][0] : constants.AddressZero;

    const donkeyStakingInterface = new utils.Interface(abi)

    const donkeyStakingContract = new Contract(
        donkeyStakingContractAddress,
        donkeyStakingInterface
    )

    const { send: stakeTokensSend, state: stakeTokensState} = 
        useContractFunction(donkeyStakingContract, "stakeTokens", {
            transactionName: "Stake tokens",
    })

    const donkeyTokenInterface = new utils.Interface(DonkeyToken.abi)
    const donkeyTokenContract = new Contract(donkeyTokenAddress, donkeyTokenInterface)

    const { send: approveDonkeyTokenSend, state: approveDonkeyTokenState} = 
        useContractFunction(donkeyTokenContract, "approve", {
            transactionName: "Approve Donkey Token Transfer",
        })

    const [ amountToStake, setAmountToStake] = useState("0")

    useEffect(() => {
        if(approveDonkeyTokenState.status === "Success") {
            stakeTokensSend(amountToStake, donkeyTokenAddress)
        }
    }, [approveDonkeyTokenState, amountToStake, donkeyTokenAddress])

    const send = (amount: string) => {
        setAmountToStake(amount)
        return approveDonkeyTokenSend(donkeyStakingContractAddress, amount)
    }

    const [state, setState] = useState(approveDonkeyTokenState)

    useEffect(() => {
        if (approveDonkeyTokenState.status === "Success") {
            setState(stakeTokensState)
        } else {
            setState(approveDonkeyTokenState)
        }
    }, [approveDonkeyTokenState, stakeTokensState])

    return { send, state}


}
