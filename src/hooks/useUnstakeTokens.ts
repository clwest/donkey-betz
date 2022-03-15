import { useContractFunction, useEthers } from "@usedapp/core";
import DonkeyStaking from "../artifacts/contracts/DonkeyStaking.json";
import {utils, constants,} from "ethers";
import {Contract} from "@ethersproject/contracts"
import networkMapping from "../artifacts/deployments/map.json";

export const useUnstakeTokens = () => {
    const {chainId} = useEthers()

    const {abi} = DonkeyStaking;
    const donkeyStakingContractAddress = chainId ? networkMapping[String(chainId)]["DonkeyStaking"][0] : constants.AddressZero;

    const donkeyStakingInterface = new utils.Interface(abi);

    const donkeyStakingContract = new Contract(
        donkeyStakingContractAddress,
        donkeyStakingInterface,
    )

    return useContractFunction(donkeyStakingContract, "unstakeTokens", {
        transactionName: "Unstake Tokens",
    })
}