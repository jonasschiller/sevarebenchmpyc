#!/bin/bash
# shellcheck disable=SC1091,2154

#
# Script is run locally on experiment server.
#

# exit on error
set -e
# log every command
set -x

REPO_DIR=$(pos_get_variable repo_dir --from-global)
timerf="%M (Maximum resident set size in kbytes)\n%e (Elapsed wall clock time in seconds)\n%P (Percent of CPU this job got)"
experiment=$1
player=$2
environ=""
# test types to simulate changing environments like cpu frequency or network latency
read -r -a types <<< "$3"
network="$4"
partysize=$5
# experiment type to allow small differences in experiments
etype=$6
# default to etype 1 if unset
etype=${etype:-1}

cd "$REPO_DIR"/experiments || exit


## Implement verification run so it can be benchmarked on the same parameters
## This will also enable the verify results function

####
#  environment manipulation section start
####
# shellcheck source=../host_scripts/manipulate.sh
source "$REPO_DIR"/host_scripts/manipulate.sh

case " ${types[*]} " in
    *" CPUS "*)
        limitCPUs;;&
    *" RAM "*)
        limitRAM;;&
    *" QUOTAS "*)
        setQuota;;&
    *" FREQS "*)
        setFrequency;;&
    *" BANDWIDTHS "*)
        # check whether to manipulate a combination
        case " ${types[*]} " in
            *" LATENCIES "*)
                setLatencyBandwidth;;
            *" PACKETDROPS "*) # a.k.a. packet loss
                setBandwidthPacketdrop;;
            *)
                limitBandwidth;;
        esac;;
    *" LATENCIES "*)
        if [[ " ${types[*]} " == *" PACKETDROPS "* ]]; then
            setPacketdropLatency
        else
            setLatency
        fi;;
    *" PACKETDROPS "*)
        setPacketdrop;;
esac

####
#  environment manipulation section stop
####

log=testresults
touch "$log"

success=true

pos_sync --timeout 300

# Some protocols are only for 2,3 or 4 parties
# they imply the flag -N so it's not allowed
extraflag="-N $partysize"
# need to skip for some nodes
skip=false

# Format Parameter String use -P addr:port option per party
partystring=""
for i in $(seq 2 $((partysize+1))); do
    partystring+=" -P 10.10."$network"."$i":23000"
done


#bash "$REPO_DIR"/experiments/multiplication/generateInput.sh "$size" "$partysize" "$player" "$REPO_DIR"/Data/Input.txt
# run the SMC protocol
$skip || /usr/bin/time -f $timerf python /root/sevarebenchmpyc/experiments/"$EXPERIMENT".py $partystring -I $player &> "$log" || success=false

pos_upload "$log"

#abort if no success
$success

pos_sync



####
#  environment manipulation reset section start
####

case " ${types[*]} " in

    *" FREQS "*)
        resetFrequency;;&
    *" RAM "*)
        unlimitRAM;;&
    *" BANDWIDTHS "*|*" LATENCIES "*|*" PACKETDROPS "*)
    	resetTrafficControl;;&
    *" CPUS "*)
        unlimitCPUs
esac

####
#  environment manipulation reset section stop
####

pos_sync