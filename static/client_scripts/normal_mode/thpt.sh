#!/bin/bash


#
#   THROUGHPUT TEST
#

export _rtt="$1"
export _rwnd="$2"
export _ideal="$3"
export _ip="$4" 
export _port="$5"
export _mode="$6"
if [[ -z "$_rtt" || -z "$_ip" || -z "$_port" || -z "$_rwnd" || -z "$_ideal" || -z "$_mode" ]]
then
echo "Normal Mode Throughput Test"
echo "Usage: ./thpt.sh <rtt> <rwnd> <ideal> <ip> <port>"
echo "<rtt> in milliseconds"
echo "<rwnd> in KB"
echo "<ideal> subscription plan in Mbps"
echo "<ip> in server ip"
echo "<port> provided port by server"
echo "<mode> normal/reverse"
echo "Example: ./thpt.sh 30 2000 100 127.0.0.1 8888 normal"
exit 1;

fi

# iperf3 
# | extract results line 

# ORIGINAL IMPLEMENTATION (SUBJECT TO REVIEW)
#THPT=$(iperf3 --client $_ip --port $_port --time 5 --window $_rwndK --format m --bandwidth 100M)
if [[ "$_mode" = "normal" ]];
then
  _mode="";
elif [[ "$_mode" = "reverse" ]];
then
  _mode="--reverse";
else
  echo "invalid mode"
  exit 1;
fi

OUT=$(iperf3 $_mode --client $_ip --port $_port --time 10 --format m --bandwidth 100M --json \
  | jq '.end | {"bytes" : .sum_sent.bytes, "thpt" : .sum_sent.bits_per_second} + { "mean_rtt" : .streams[].sender.mean_rtt }') 

AVE_THPT=$(echo $OUT | jq '.thpt/1000000')
DATA_SENT=$(echo $OUT | jq '.bytes/1000000')
AVE_RTT=$(echo $OUT | jq '.mean_rtt/1000')

if [[ -z "$AVE_THPT" || -z "$DATA_SENT" || -z "$AVE_RTT" ]]
then
echo "Throughput Test failed"
exit 1;
fi

echo "Total Data Sent: $DATA_SENT Mbytes"
echo "thpt_avg: $AVE_THPT Mbits/sec"
echo "thpt_ideal: $_ideal Mbits/sec"
echo "ave_rtt: $AVE_RTT ms"

touch thpt_extract.py
cat << EOF > thpt_extract.py

import sys
data_sent= float(sys.argv[1])
ideal_thpt= float(sys.argv[2])
actual_thpt= float(sys.argv[3])
base_rtt= float(sys.argv[4])
ave_rtt= float(sys.argv[5])
ideal_time = data_sent * 8 / ideal_thpt
actual_time = 10
ttr = actual_time / ideal_time
buf_del = ( (ave_rtt - base_rtt) / base_rtt ) * 100
print("transfer_avg: 10 seconds")
print("transfer_ideal: " + str(ideal_time)+" seconds")
print("tcp_ttr: " + str(ttr))
print("buffer_delay: " + str(buf_del)+"%")

EOF

python thpt_extract.py $DATA_SENT $_ideal $AVE_THPT $_rtt $AVE_RTT
rm thpt_extract.py

