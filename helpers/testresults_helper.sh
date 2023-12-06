#!/bin/bash
# shellcheck disable=SC2154,2034

# where we find the experiment results
resultpath="$RPATH/${NODES[0]}/"

# verify testresults by comparing to verification run results
verifyExperiment() {
            
# get pos filepath of the measurements for the current loop
experimentresult=$(find "$resultpath" -name "testresults" -print -quit)
verificationresult=$(find "$resultpath" -name "measurementlog" -print -quit)

# check existance of files
if [ ! -f "$experimentresult" ] || [ ! -f "$verificationresult" ]; then
    styleOrange "  Skip File not found error: $experimentresult"
    continue 2
fi

# verify experiment result - call experiment specific verify script
chmod +x experiments/"$EXPERIMENT"/verify.py
match=$(experiments/"$EXPERIMENT"/verify.py "$experimentresult" "$verificationresult")
if [ "$match" != 1 ]; then
    styleOrange "  Skip $match at $experimentresult";
    continue 2;
fi
((++i))


# only pass if while-loop actually entered
okfail ok "  verified - test passed"

}

############
# Export experiment data from the pos_upload-ed logs into two tables
############
exportExperimentResults() {

    # set up location
    datatableShort="$EXPORTPATH/data/short_results.csv"
    datatableFull="$EXPORTPATH/data/full_results.csv"
    mkdir -p "$datatableShort"
    rm -rf "$datatableShort"

    dyncolumns=""
    # get the dynamic column names from the first .loop info file
    loopinfo=$(find "$resultpath" -name "*loop" -print -quit)
    
    # check if loop file exists
    if [ -z "$loopinfo" ]; then
        okfail fail "nothing to export - no loop file found"
        return
    fi

    for columnname in $(jq -r 'keys_unsorted[]' "$loopinfo"); do
        dyncolumns+="$columnname"
        case "$columnname" in
            freqs) dyncolumns+="(GHz)";;
            quotas|packetdrops) dyncolumns+="(%)";;
            latencies) dyncolumns+="(ms)";;
            bandwidths) dyncolumns+="(Mbs)";;
        esac
        dyncolumns+=";"
    done

    # generate header line of data dump with column information
    basicInfo1="program;partysize;"
    basicInfo2="${dyncolumns},runtime_internal(s);ALLdataSent(MB)"
    
    echo -e "${basicInfo1}${basicInfo2}" > "$datatableShort"
    echo -e "${basicInfo1}${basicInfo2}" > "$datatableFull"

    i=0
    # get loopfile path for the current variables
    loopinfo=$(find "$resultpath" -name "*$i.loop*" -print -quit)
    echo " exporting"
    # while we find a next loop info file do
    while [ -n "$loopinfo" ]; do
        loopvalues=""
        # extract loop var values
        for value in $(jq -r 'values[]' "$loopinfo"); do
            loopvalues+="$value;"
        done

        # the actual number of participants
        partysize="${#NODES[*]}"
        
        # get pos filepath of the measurements for the current loop
        # currently no compile info is stored for mpyc as it is not relevant for benchmark
        # time is only extracted from text of testresults file
        #compileinfo=$(find "$resultpath" -name "measurementlog_run*$i" -print -quit)
        runtimeinfo=$(find "$resultpath" -name "testresults_run*$i" -print -quit)
        if [ ! -f "$runtimeinfo" ]; then
            styleOrange "    Skip - File not found error: runtimeinfo or compileinfo"
            continue 2
        fi

        ## Minimum result measurement information
        ######
        # extract measurement
        runtimeint=$(grep "elapsed time:" "$runtimeinfo" | awk '{print $6}') | cut -d'|' -f 1
        globaldataSent=$(grep "bytes sent: " "$runtimeinfo" | awk '{print $10}')

        # put all collected info into one row (Short)
        basicInfo="${EXPERIMENT};$partysize;"
        echo -e "$basicInfo;$loopvalues$runtimeint;$globaldataSent" >> "$datatableShort"


        measurementvalues="$runtimeint;$globaldataSent"

        # put all collected info into one row (Full)
        echo -e "$basicInfo;$compilevalues;$loopvalues$measurementvalues" >> "$datatableFull"

        # locate next loop file
        ((++i))
        loopinfo=$(find "$resultpath" -name "*$i.loop*" -print -quit)
    done
    # check if there was something exported
    rowcount=$(wc -l "$datatableShort" | awk '{print $1}')
    if [ "$rowcount" -lt 2 ];then
        okfail fail "nothing to export"
        rm "$datatableShort"
        return
    fi

    # create a tab separated table for pretty formating
    # convert .csv -> .tsv
    column -s ';' -t "$datatableShort" > "${datatableShort::-3}"tsv
    column -s ';' -t "$datatableFull" > "${datatableFull::-3}"tsv
    okfail ok "exported short and full results (${datatableShort::-3}tsv)"


    # Add speedtest infos to summaryfile
    {
        echo -e "\n\nNetworking Information"
        echo "Speedtest Info"
        # get speedtest results
        for node in "${NODES[@]}"; do
            grep -hE "measured speed|Threads|total" "$RPATH/$node"/speedtest 
        done
        # get pingtest results
        echo -e "\nLatency Info"
        for node in "${NODES[@]}"; do
            echo "Node $node statistics"
            grep -hE "statistics|rtt" "$RPATH/$node"/pinglog
        done
    } >> "$SUMMARYFILE"

    # push to measurement data git
    repourl=$(grep "repoupload" global-variables.yml | cut -d ':' -f 2-)
    # check if upload git does not exist yet
    if [ ! -d git-upload/.git ]; then
        # clone the upload git repo
        # default to trust server fingerprint authenticity (usually insecure)
        GIT_SSH_COMMAND='ssh -o StrictHostKeyChecking=accept-new' git clone "${repourl// /}" git-upload
    fi

    echo " pushing experiment measurement data to git repo$repourl"
    cd git-upload || { warning "${FUNCNAME[0]}:${LINENO} cd into gitrepo failed"; return; }
    {
        # a pull is not really required, but for small sizes it doesn't hurt
        git pull
        # copy from local folder to git repo folder
        [ ! -d "${EXPORTPATH::-12}" ] && mkdir results/"${EXPORTPATH::-12}"
        cp -r ../"$EXPORTPATH" "${EXPORTPATH::-12}"
        git add . 
        git commit -a -m "script upload"
        git push 
    } &> /dev/null ||{ warning "${FUNCNAME[0]}:${LINENO} git upload failed"; return; }
        okfail ok " upload success" 
}

infolineparser() {
    # infolineparser $1=regex $2=var-reference $3=column1 $4=column2 $5=column3
    regex="$1"
    # get reference
    declare -n target="$2"

    MB=$(grep "$regex" "$runtimeinfo" | head -n 1 | cut -d ' ' -f "$3")
    Rounds=$(grep "$regex" "$runtimeinfo" | head -n 1 | cut -d ' ' -f "$4")
    Sec=$(grep "$regex" "$runtimeinfo" | head -n 1 | cut -d ' ' -f "$5")
    target="${MB:-NA};${Rounds:-NA};${Sec:-NA}"
}

