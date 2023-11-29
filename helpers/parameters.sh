#!/bin/bash
# shellcheck disable=SC2034,2154

usage() {
    styleCyan "$0: $1"
    echo
    echo "Options: { -e[xperiment] | -n[odes] | -p[rotocols] | -i[nput] | -c[pu] |"
    echo "           -q(--cpuquota) | -f[req] | -r[am] | -l[atency] | -b(andwidth)} |"
    echo "           -d(--packetdrop)"
    echo -e "\nRun '$0 --help' for more information.\n"
    echo "Available experiments:"
	ls experiments
    echo -e "\nAvailable NODES:"
	# xargs replaces '\n' with ' '
	pos no li | grep -E "$(whoami)|None" | awk '{print $1}' | xargs
    exit 1
}

help() {
	echo "$0 - run SMC experiments with MP-SPDZ protocol and POS testbed environment"
    echo "Example:  ./$0 -e 31_scalable_search -p shamir,atlas -n valga,tapa,rapla -i 10,20,...,100 -q 20,40,80 -f 1.9,2.6"
    echo
    echo "<Values> supported are of the form <value1>[,<value2>,...] or use \"...\" to specify the range"
    echo "       [...,<valuei>,]<start>,<next>,...,<stop>[,valuek,...], with increment steps <next>-<start>"
    echo -e "\nOptions (mandatory)"
    echo " -e, --experiment     experiment to run"
    echo " -n, --nodes          nodes to run the experiment on of the form <node1>[,<node2>,...]"
    echo " -i, --input          input sizes, with <Values>"
    echo -e "\nOptions (optional)"
    echo "     --etype          experiment type, if applicable, specified with a code"
    echo "     --config         config files run with <path> as parameter, nodes can be given separatly"
    echo "                      allowed form: $0 --config file.conf [nodeA,...]"
    echo -e "\nManipulate Host Environment (optional)"
    echo " -c, --cpu            cpu thread counts, with <Values>"
    echo " -q, --cpuquota       cpu quotas in % (10 < quota), with <Values>"
    echo " -f, --freq           cpu frequencies in GHz (e.g. 1.7), with <Values>"
    echo " -r, --ram            limit max RAM in MiB (e.g. 1024), with <Values>, /dev/nvme0n1 required"
    echo "     --swap           set secondary memory swap size in MiB, one value, SSD /dev/nvme0n1 required"
    echo "                      mandatory with -r to allow paging/swaping (default 4096)"
    echo "                      Warning: setting this too small will break the entire run at some point"
    echo -e "\nManipulate Network Environment (optional)"
    echo " -l, --latency        latency of network in ms, with <Values>"
    echo " -b, --bandwidth      bandwidth of network in MBit/s, with <Values>"
    echo " -d, --packetdrop     packet drop/loss in network in %, with <Values>"
	echo -e "\nAvailable experiments:\n"
	ls experiments
	echo -e "\nAvailable NODES:\n"
	# xargs replaces '\n' with ' '
	pos no li | grep -E "$(whoami)|None" | awk '{print $1}' | xargs
	exit 0
}

setArray() { # load array $1 reference with ,-seperated values in $2
    local -n array="$1"     # get array reference
    set -f                  # avoid * expansion
    IFS="," read -r -a array <<< "$2"
    for element in "${array[@]}"; do
        echo "$element"
    done
}

TEMPFILES=()
ALLOC_ID=""
EXPORTPATH="results/$(date +20%y-%m)/$(date +%d_%H-%M-%S)"
# pos_upload resultspath
RPATH=""
SUMMARYFILE=""
POS=pos
IMAGE=debian-bullseye
SECONDS=0
RUNSTATUS="${Red}fail${Stop}"
# this is required for the config support logic
CONFIGRUN=false

experiment=""
runflags=""
NODES=()
INPUTS=()
CPUS=()
QUOTAS=()
FREQS=()
LATENCIES=()
BANDWIDTHS=()
PACKETDROPS=()
RAM=()
SWAP=""
TTYPES=()
PIDS=()
# create a random network number to support multiple experiment runs 
# on the same switch.   Generate random number  1 < number < 255
NETWORK=$((RANDOM%253+2))

 # Experiment run summary  information output
SUMMARYFILE="$EXPORTPATH/run-summary.dat"
mkdir -p "$EXPORTPATH" && rm -rf "$SUMMARYFILE"
{
    echo "  Setup:"
    echo "    Experiment = $EXPERIMENT $ETYPE"
    echo "    Nodes = ${NODES[*]}"
    echo "    Internal network = 10.10.$NETWORK.0/24"
    echo "    Inputs = ${INPUTS[*]}"
    echo "    Testtypes:"
    for type in "${TTYPES[@]}"; do
        declare -n ttypes="${type}"
        echo -e "      $type\t= ${ttypes[*]}"
    done
    echo "  Summary file = $SUMMARYFILE"
    } | tee "$SUMMARYFILE"

# Parsing inspired from https://stackoverflow.com/a/29754866
# https://gist.github.com/74e9875d5ab0a2bc1010447f1bee5d0a

setParameters() {
    echo "Start"
    # verify if getopt is available
    getopt --test > /dev/null
    [ $? -ne 4 ] && { error $LINENO "${FUNCNAME[0]}(): getopt not available 
        for parsing arguments."; }
    # define the flags for the parameters
    # ':' means that the flag expects an argument.
    SHORT=n:,e:,h
    LONG=nodes:,experiment:,help

    PARSED=$(getopt --options ${SHORT} \
                    --longoptions ${LONG} \
                    --name "$0" \
                    -- "$@") || { error $LINENO "${FUNCNAME[0]}(): getopt failed parsing options"; }

    eval set -- "${PARSED}"
    while [ $# -gt 1 ]; do
        #echo "parsing arg: $1 $2"
        case "$1" in
            -h|--help)
                help;;
            -n|--nodes) 
                setArray NODES "$2"
                shift;;
            -e|--experiment)
                experiment="$2"
                shift;;
            *) error $LINENO "${FUNCNAME[0]}(): unrecognized flag $1 $2";;
        esac
        shift || true      # skip to next option-argument pair
    done
    # node already in use check
    #nodetasks=$(pgrep -facu "$(id -u)" "${NODES[0]}")
    #[ "$nodetasks" -gt 10 ] && error $LINENO "${FUNCNAME[0]}(): it appears host ${NODES[0]} is currently in use"
}
