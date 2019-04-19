# This code contains example of fetching data via CRM api
#
# This code is based on top of multiple web resources mainly from following web reference
# https://alexanderdevelopment.net/post/2016/11/27/dynamics-365-and-python-integration-using-the-web-api/
# https://community.dynamics.com/crm/b/dynamicscrmdevdownunder/archive/2017/01/15/executing-large-fetchxml-with-webapi
# 

import requests
import json
import pandas as pd
import urllib

from adal import AuthenticationContext


# Azure App which need to be granted with Dynamics 365 permission on Azure portal
clientAppId = [AppId]
clientAppKey = [AppKey]

# Request Azure access token
requestURL= 'https://[domain].dynamics.com/'
auth_context = AuthenticationContext("https://login.microsoftonline.com/[domain]")
token_response = auth_context.acquire_token_with_client_credentials(requestURL,clientAppId, clientAppKey)

# Example of CRM API
crmwebapi = 'https://[domain].api.crm.dynamics.com/api/data/v9.0' 
crmwebapiquery = '/contacts'

#################################################################
# 1. Direct query example
#   https://docs.microsoft.com/en-us/dynamics365/customer-engagement/developer/webapi/query-data-web-api
# example: https://[domain].api.crm.dynamics.com/api/data/v9.0/contacts?$select=fullname,contactid&$top=10

# params = '$select=fullname,contactid&$top=10'

#################################################################
# 2. Fetch data via fetchXml as parameter
#   fetchXml can be generated from advance search page on CRM site
# exmaple: https://[domain].api.crm.dynamics.com/api/data/v9.0/contacts?fetchXml=%3Cfetch+count%3D%2210%22+%3E%3Centity+name%3D%22
#          contacts%22+%3E%3Cattribute+name%3D%22fullname%22+%2F%3E%3Cattribute+name%3D%22contactid%22+%2F%3E%3C%2Fentity%3E%3C%2Ffetch%3E

fetchXml='''
<fetch count="10" >
  <entity name="contacts" >
    <attribute name="fullname" />
    <attribute name="contactid" />
  </entity>
</fetch>'''

queryparams={ 'fetchXml': fetchXml.replace("\n", "").replace("  ", "") }
params = urllib.parse.urlencode(queryparams)

#################################################################
# 3. Fetch data via saved/user query
# API to list saved/user query id
# https://[domain].api.crm.dynamics.com/api/data/v9.0/savedqueries?$select=name,savedqueryid
# https://[domain].api.crm.dynamics.com/api/data/v9.0/userqueries?$select=name,userqueryid
# exmaple: https://[domain].api.crm.dynamics.com/api/data/v9.0/contacts?userQuery=00000000-0000-0000-0000-000000000000

userqueryId ='[userqueryid]' # user Query
userqueryparams = { 'userQuery': userqueryId }
params = urllib.parse.urlencode(userqueryparams) 

#################################################################
# Construct query url

url = crmwebapi+crmwebapiquery+"?%s" % params

def getValue(valueName, data):
    return data[valueName] if valueName in x.keys() else ''
    
try:
    accesstoken = token_response.get('accessToken')
except KeyError as e:
    #handle any missing key errors
    print('Could not get access token')
    print(str(e))

if(accesstoken!=''):

    # Request header
    crmrequestheaders = {
        'Authorization': 'Bearer ' + accesstoken,
        'OData-MaxVersion': '4.0',
        'OData-Version': '4.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=utf-8',
        # https://docs.microsoft.com/en-us/dynamics365/customer-engagement/developer/webapi/web-api-query-data-sample#bkmk_filterPagination
        # 'Prefer': 'odata.maxpagesize=100', 
        'Prefer': 'odata.include-annotations=OData.Community.Display.V1.FormattedValue' #Include formatted values
    }
 
    # Http Get data over API
    crmres = requests.get(url, headers=crmrequestheaders)

     # Get the response json
    crmresults = crmres.json()

    # Create panda dataframe with result
    results=pd.DataFrame(columns=['FullName', 'ContactId'])
    
    # Append result
    for x in crmresults['value']:
        result={}
        result['FullName']=getValue('fullname', x)
        result['ContactId']=getValue('contactid', x)
        results=results.append(result,ignore_index=True)

