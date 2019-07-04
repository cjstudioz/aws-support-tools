868982

# Background / Context
I understand the python ecosystem well. I’m relatively familiar with AWS’s core offerings and have worked with many equivalent proprietary components. However, I have less experience with how well these components integrate with python in a python centric ecosystem. 
By that I don’t just mean the availability of a python API or boto3, but more importantly 
-	is the api feature set complete and robust? 
-	Are there impedance mismatches between the python API and the AWS components? 
-	Are the APIs / usages pythonic such that my code remains concise and readable?

<response / comment> python is 2nd most popular languge after Java in AWS space. therefore boto3 ando ther python SDKs get feature updates frequently. caveat, the python APIs are much higher level compared to the Java and CLI ones.

## High Level  Considerations 
A non-exhaustive list of design decisions we need to make before we can evolve our codebase into the next phase.
1.	Which AWS components integrate better with python and which have been known to struggle. 
2.	Should we consider other languages for the latter in a micro-service decentralized architecture?
3.	Should I use the core AWS offering or frameworks above them? if the latter, should I use the internal or external offering?
e.g. 
Beanstalk vs Kubernetese + Docker vs hosting my own containers / schedulers in raw EC2 VMs
Or
using Chalice or Serverless framework instead of lambdas directly.

NOTE: by python I do not mean Django. 


## Workloads 
Many our workloads can be broken down into 3 types:
a)	Internal (non api gateway) polling processes with fixed workload (no elasticity or spikes)
b)	very sporadic lightweight external API calls.2 -3 calls per day with no foreseeable scaling. Could be triggered by end-user or internal event driven
c)	end user driven workload which with reasonable predictability e.g. seasonal / peak time of day usage. Which will first start at under 1000 requests per day but potentially scale to hundreds of thousands to a million requests per day per endpoint.

# Specific Questions:
Bearing the context above in mind, I'd like to discuss the specifics below 

## AWS Lambdas:
Pros and Cons of Serverless framework vs Chalice. If we are purely python based, can you make a recommendation based on projected AWS investment.
Does AWS support both equally?

<response> mike to follow up with chalice and serverless team on roadmap for each and come back with Pros and cons

## Common Libraries
What is the recommendation for deploying a common python library to a single place which other lambdas, beanstalk and aws components can referece. (these are libraries, not microservice endpoints)

<response> no way of sharing common libraries across all components. 
  use layers within lambda (but not yet supported by chalice or serverless) Mike to find out timelines as part of roadmap,
  beanstalk has no off the shelf solution, stick to git submodules. can use AMI or docker images.
  Industry is moving towards containerized solutions

## Monitoring:
What is AWS’s recommendation for monitoring and alerting, please compare internal offering vs Splunk, ELK, datadog.

<response> they don't have detailed knowledge of monitoring offering specifics in AWS marketplace. we have to appraoch Splunk and Datadog ourselves to see if there are on prem solutions. for now, using boto3 + cloudwatch will suffice. I will look into examples.

## CI / CD Pipeline:
We’ve decided to use Azure Devops (previously VSTS) for task / issue management, sprint planning, and version control repositories. While we know they fully support integration with AWS, I’d like to know if this adds additional complexity or requires more overhead compared to using Github / Jenkins / Travis / AWS Code Commit / Code Deploy. Please compare and contrast these options within the AWS ecosystem for us especially within the Lambda, Beanstalk, EC2, RDS and API Gateway space.

<response> Mike is not familiar with Azure devops and will tap internal contacts for more info. the AWS code commit/ deploy etc suite has tighter integration with their components e.g. autosclaing groups. their recommendation if we're starting from scratch is to use their code tool suite. but it is not a strong preference.

## VPC / inter cloud vendor communication:
So far I’ve tried to keep all data within a single VPC all inside the AWS ecosystem, however, we may need to move data to externally hosted services e.g. log aggregation to Splunk or reporting database to IBM Snowflake. Can we have a discussion around both commercial and technical considerations around moving data between cloud providers?


