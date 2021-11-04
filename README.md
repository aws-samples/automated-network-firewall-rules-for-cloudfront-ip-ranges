## Automated Network Firewall Rules for CloudFront IP Ranges

Amazon CloudFront is a content delivery network (CDN) that provides a globally-distributed network of proxy servers that cache content, such as web videos or other bulky media, more locally to consumers, thus improving access speed for downloading the content. One option to secure your content delivery origins in cloud such as EC2 instances, web server containers, S3 buckets, API Gateways etc. is to utilize AWS Network Firewall by blocking unwanted traffic.

To ensure that the only allowed traffic source is CloudFront IP ranges, we need to specify these IP ranges in the firewall rules, and specify “Allow” as an action. However, CloudFront IP ranges change constantly and it would be both cumbersome and unsafe to try updating firewall rules manually as it is prone to human mistake.

For that reason, this artifact focuses on creating automated network firewall rules utilizing the various AWS services such as Simple Notification Service, Parameter Store, and Lambda. 

![image](https://user-images.githubusercontent.com/93626739/140253139-ab8bd894-4322-4567-ba53-f59086e5ae30.png)

As shown in the diagram above, it is a relatively simple architecture which starts with an SNS topic managed by Amazon, feeding a JSON file that includes the updated IP ranges of all Amazon services to our Lambda Python function. Lambda function then parses this file and filters out the CloudFront IP ranges, and creates the rule group accordingly along with the destination IP ranges provided by the user (you). 


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

