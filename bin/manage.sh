#!/bin/bash

kill_all() {

        cd $MOS_PATH/etc/active

        for i in *.NIC; do
                [ -f "$i" ] || break
                ip link del $i
                rm $i
        done

        for i in *.BR; do
                [ -f "$i" ] || break
                ip link del $i
                rm $i
        done


        for i in *.PID; do
                [ -f "$i" ] || break
                cat $i | xargs kill
                rm $i
        done

        nft flush ruleset

}
