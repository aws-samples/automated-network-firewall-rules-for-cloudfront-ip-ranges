import json
import boto3
import os
import logging
import urllib.request, urllib.error, urllib.parse
import hashlib
import botocore.exceptions

ssmClient = boto3.client('ssm')
SERVICE = os.getenv('SERVICE', "CLOUDFRONT")
RULE_GROUP_CAP = 1000
NRULES=500
NameParam = ssmClient.get_parameter(Name='RuleGroupName')
NAME = NameParam['Parameter']['Value']
DESTLIST = ssmClient.get_parameter(Name='DestinationRanges')

def lambda_handler(event, context):
    
    global NAME
    client = boto3.client('network-firewall')
    
    # Set up logging
    if len(logging.getLogger().handlers) > 0:
        logging.getLogger().setLevel(logging.ERROR)
    else:
        logging.basicConfig(level=logging.DEBUG)
    
    # SNS message notification event when the ip ranges document is rotated
    message = json.loads(event['Records'][0]['Sns']['Message'])
    
    # Get the updated IP ranges from the link in the SNS message
    ip_ranges = json.loads(get_ip_groups_json(message['url']))
    cf_ranges = get_ranges_for_service(ip_ranges, SERVICE)
    
    # Try to create the new rule group. If it exists, get the update token and update the list.
    try:
        create_rule_group(NAME, cf_ranges)
    except client.exceptions.InvalidRequestException:
        updateToken = get_update_token(NAME)
        update_rule_group(NAME, cf_ranges, updateToken)
        
# Helper function to get the update token
def desc_rule_group(name):

    client = boto3.client('network-firewall')
    desc = client.describe_rule_group(
                                    RuleGroupName=name,
                                    Type='STATELESS')
    return desc
    
# Returns the update token
def get_update_token(ruleGroupName):
    
    descResponse = desc_rule_group(ruleGroupName)
    updateToken = descResponse['UpdateToken']
    
    return updateToken

# Creates a new rule group
def create_rule_group(name, ranges):

    client = boto3.client('network-firewall')
    global RULE_GROUP_CAP
    
    createRuleGr = client.create_rule_group(
        RuleGroupName=name,
        Type='STATELESS',
        Capacity=int(RULE_GROUP_CAP),
        RuleGroup=
        {
            'RulesSource': 
            {
                'StatelessRulesAndCustomActions': 
                {
                    'StatelessRules': generate_rules(ranges),
                    'CustomActions': []
                }
            }
        }
    )

# Updates the existing rule group with the new set of IP ranges
def update_rule_group(name, ranges, updateToken):

    client = boto3.client('network-firewall')
    global RULE_GROUP_CAP
    
    updateRuleGr = client.update_rule_group(
        UpdateToken=updateToken,
        RuleGroupName=name,
        Type='STATELESS',
        RuleGroup=
        {
            'RulesSource': 
            {
                'StatelessRulesAndCustomActions': 
                {
                    'StatelessRules': generate_rules(ranges),
                    'CustomActions': []
                }
            }
        }
    )
 
# Helper function for the create and update functions for creating multiple rules if needed
def generate_rules(ranges):

    global NRULES
    global DESTLIST
    rules = []
    priority=0
    split_ranges = range_splitter(ranges, NRULES)
    # print("split_ranges: "+str(split_ranges))

    for currentranges in split_ranges:
        # print("currentranges"+str(currentranges))
        priority+=1
        rules.append(
            {
                'Priority': priority,
                "RuleDefinition":
                {
                    "Actions": ["aws:allow"],
                    "MatchAttributes":
                    {
                        "Destinations": generate_destlist(DESTLIST),
                        "Sources": generate_sourcelist(currentranges)
                    }
                }
            }
        )
    
    # print("rules"+str(rules))
    return rules

# Helper function for the create and update functions for creating multiple destinations in one rule if needed
def generate_destlist(ranges):
    destList = ranges['Parameter']['Value'].split(",")
    destinations = []
    
    for range in destList:
        noSpace = range.replace(" ","")
        stripped = noSpace.strip()
        destinations.append(
            {
                "AddressDefinition": stripped
            }
        )
        
    return destinations

# Helper function for the create and update functions for creating multiple sources in one rule if needed
def generate_sourcelist(ranges):
    # print("generate_sourcelistinput:" + str(ranges))
    sources = []
    
    for range in ranges:
        sources.append(
            {
                "AddressDefinition": range
            }
        )
        
    return sources

# Splits the set of IP ranges if they need to be implemented in multiple rules instead of one
def range_splitter(ranges, splitby):
    
    split=[]
    
    for x in range(0, len(ranges), splitby):
        each_chunk = ranges[x: splitby+x]
        split.append(each_chunk)
        # print(each_chunk)
        
    return split

# Pulls the IP groups from the url
def get_ip_groups_json(url):
    
    logging.info("Updating from " + url)

    response = urllib.request.urlopen(url)
    ip_json = response.read()

    return ip_json

# Pulls the IP ranges for a specific service (e.g.CloudFront)
def get_ranges_for_service(ranges, service):
    
    service_ranges = list()
    
    for prefix in ranges['prefixes']:
        if prefix['service'] == service:
            service_ranges.append(prefix['ip_prefix'])
    
    logging.info(('Found ' + service + ' ranges: ' + str(len(service_ranges))))
    return service_ranges