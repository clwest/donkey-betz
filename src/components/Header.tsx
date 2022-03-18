import {useEthers} from "@usedapp/core";
import { Button, makeStyles } from "@material-ui/core";
import rebel from "../rebel.png";

const useStyles = makeStyles((theme) => ({
    container: {
        padding: theme.spacing(2),
        display: "flex",
        justifyContent: "flex-end",
        gap: theme.spacing(2)
    },
    btn: {
        backgroundColor: "#C3DF10",
        color: "black",
    },
    btn2: {
        backgroundColor: "#C3DF10",
        color: "black",
    }
}))

export const Header = () => {
    const classes = useStyles();

    const {account, activateBrowserWallet, deactivate } = useEthers();

    const isConnected = account !== undefined

    return (
        <div className={classes.container}>
            {isConnected ? (
                <>
            
                <Button className={classes.btn} color="primary" variant="contained">
                    {`${account?.slice(0, 4)}...${account?.slice(-3)}`}
                </Button>
                <Button className={classes.btn2} color="primary" variant="contained" onClick={deactivate}>
                    Disconnect
                </Button>
                </>
            ) : (
                <Button className={classes.btn} color="primary" variant="contained" onClick={() => activateBrowserWallet()}>
                    Connect
                </Button>
            )
        }

        </div>
    )


} 