# # # DISTRIBUTION STATEMENT A. Approved for public release: distribution unlimited.
# # # 
# # # Author:
# # # Naval Research Laboratory, Marine Meteorology Division
# # # 
# # # This program is free software: you can redistribute it and/or modify it under
# # # the terms of the NRLMMD License included with this program.  If you did not
# # # receive the license, see http://www.nrlmry.navy.mil/geoips for more
# # # information.
# # # 
# # # This program is distributed WITHOUT ANY WARRANTY; without even the implied
# # # warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# # # included license for more details.

    echo `date` " Running " `basename $call`
    echo $call

    # Set a unique log file for the current script - this allows us to check output from individual calls.
    script_path=`echo $call | cut -d " " -f1`
    script_args=`echo $call | cut -d " " -f2-`
    # If there are no arguments, script_args will just be the path
    if [[ "$script_args" == "$script_path" ]]; then
        script_args=""
    else
        script_args=_${script_args// /_}
    fi
    script_name=`basename $script_path`
    script_log=${LOGFILE}_${script_name}${script_args}.log

    overall_num=$((overall_num+1))
    curr_start=`date +%s`

    echo $script_log
    $call >> $script_log 2>&1
    overall_procflow_retvals[$overall_num]=$?

    curr_end=`date +%s`
    overall_calls[$overall_num]="$call"
    overall_runtimes[$overall_num]=$((curr_end-curr_start))

    echo "" >> $LOGFILE 2>&1
    echo "" >> $LOGFILE 2>&1
    echo "$script_log" >> $LOGFILE 2>&1
    echo "" >> $LOGFILE 2>&1

    grep "BADCOMPARE " $script_log >> $LOGFILE 2>&1
    bad_compare_retval=$?
    grep "MISSINGCOMPARE " $script_log >> $LOGFILE 2>&1
    missing_compare_retval=$?
    grep "MISSINGPRODUCT" $script_log >> $LOGFILE 2>&1
    missing_product_retval=$?
    grep "FAILED INTERFACE" $script_log >> $LOGFILE 2>&1
    failed_interface_retval=$?


    grep "SUCCESSFUL COMPARISON DIR:" $script_log >> $LOGFILE 2>&1
    config_retval=$?
    grep "GOODCOMPARE " $script_log >> $LOGFILE 2>&1
    product_compare_retval=$?
    grep "FOUNDPRODUCT" $script_log >> $LOGFILE 2>&1
    cylc_test_retval=$?
    grep "SETUPSUCCESS" $script_log >> $LOGFILE 2>&1
    cylc_setup_retval=$?
    grep "SUCCESSFUL INTERFACE" $script_log >> $LOGFILE 2>&1
    success_interface_retval=$?
    
    if [[ $overall_procflow_retvals[$overall_num] == 0 && $config_retval != 0 && $product_compare_retval != 0 && $cylc_test_retval != 0 && $cylc_setup_retval != 0 && $success_interface_retval != 0 ]]; then
        echo "  FAILED Log output did not contain SUCCESSFUL COMPARISON DIR, GOODCOMPARE, FOUNDPRODUCT, SETUPSUCCESS, or SUCCESSFUL INTERFACE"
        echo "      False 0 return?"
        echo "      Please check test script to ensure output is set properly,"
        echo "      and ensure log output includes valid success strings"
        echo "  FAILED Log output did not contain SUCCESSFUL COMPARISON DIR, GOODCOMPARE, FOUNDPRODUCT, SETUPSUCCESS, or SUCCESSFUL INTERFACE" >> $LOGFILE 2>&1
        echo "      False 0 return?" >> $LOGFILE 2>&1
        echo "      Please check test script to ensure output is set properly," >> $LOGFILE 2>&1
        echo "      and ensure log output includes valid success strings" >> $LOGFILE 2>&1
        overall_procflow_retvals[$overall_num]=42
    fi
    if [[ $overall_procflow_retvals[$overall_num] == 0 && ( $bad_compare_retval == 0 || $missing_compare_retval == 0 || $missing_product_retval == 0 || $failed_interface_retval == 0 ) ]]; then
        echo "  FAILED Log output DID contain BADCOMPARE, MISSINGCOMPARE, MISSINGPRODUCT, or FAILED INTERFACE"
        echo "      False 0 return?"
        echo "      Please check test script to ensure output is set properly,"
        echo "      and ensure log output includes valid success strings"
        echo "  FAILED Log output DID contain BADCOMPARE, MISSINGCOMPARE, MISSINGPRODUCT, or FAILED INTERFACE" >> $LOGFILE 2>&1
        echo "      False 0 return?" >> $LOGFILE 2>&1
        echo "      Please check test script to ensure output is set properly," >> $LOGFILE 2>&1
        echo "      and ensure log output includes valid success strings" >> $LOGFILE 2>&1
        overall_procflow_retvals[$overall_num]=42
    fi

    echo "        Return: ${overall_procflow_retvals[-1]}"
    echo ""
