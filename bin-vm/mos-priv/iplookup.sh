# Specify DNS server
dnsserver="189.124.138.68"
# function to get IP address
function get_ipaddr {
  ip_address=""
    # A and AAA record for IPv4 and IPv6, respectively
    # $1 stands for first argument
  if [ -n "$1" ]; then
    hostname="${1}"
    if [ -z "query_type" ]; then
      query_type="A"
    fi
    # use host command for DNS lookup operations
    host -t ${query_type}  ${hostname} &>/dev/null ${dnsserver}
    if [ "$?" -eq "0" ]; then
      # get ip address
      ip_address="$(host -t ${query_type} ${hostname} ${dnsserver}| awk '/has.*address/{print $NF; exit}')"
    else
      exit 1
    fi
  else
    exit 2
  fi
# display ip
 echo $ip_address
}
hostname="${1}"
for query in "A-IPv4" "AAAA-IPv6"; do
  query_type="$(printf $query | cut -d- -f 1)"
  ipversion="$(printf $query | cut -d- -f 2)"
  address="$(get_ipaddr ${hostname})"
  if [ "$?" -eq "0" ]; then
    if [ -n "${address}" ]; then
    echo "The ${ipversion} adress of the Hostname ${hostname} is: $address"
    fi
  else
    echo "An error occurred"
  fi
done
