import React from "react";
import { Typography, makeStyles} from "@material-ui/core";

const useStyles = makeStyles((theme) => ({
    container: {
        display: "grid",
        alignItems: "center",
        justifyItems: "center",
        gridTemplateRows: "150px"
    },
}))

export const ConnectionRequireMsg = () => {
    const classes = useStyles();

    return (
        <div className={classes.container}>
            <Typography variant="h6" component="span">
                Please connect MetaMask to the Kovan Network!
            </Typography>
        </div>
    )
}