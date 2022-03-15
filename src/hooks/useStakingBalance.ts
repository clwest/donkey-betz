import { useContractCall, useEthers } from "@usedapp/core";
import DonkeyStaking from "../artifacts/contracts/DonkeyStaking.json";
import {utils, BigNumber, constants } from "ethers";
import networkMapping from "../artifacts/deployments/map.json";


export const useStakingBalance = (address: string): BigNumber | undefined => {
    const {account, chainId} = useEthers()

    const {abi} = DonkeyStaking;
    const donkeyStakingContractAddress = chainId ? networkMapping[String(chainId)]["DonkeyStaking"][0] : constants.AddressZero;

    const donkeyStakingInterface = new utils.Interface(abi);

    const [stakingBalance] =
        useContractCall({
            abi: donkeyStakingInterface,
            address: donkeyStakingContractAddress,
            method: "stakingBalance",
            args: [address, account]
        }) ?? []

    return stakingBalance;

}