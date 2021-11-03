## Automated Network Firewall Rules for CloudFront IP Ranges

Amazon CloudFront is a content delivery network (CDN) that provides a globally-distributed network of proxy servers that cache content, such as web videos or other bulky media, more locally to consumers, thus improving access speed for downloading the content. One option to secure your content delivery origins in cloud such as EC2 instances, web server containers, S3 buckets, API Gateways etc. is to utilize AWS Network Firewall by blocking unwanted traffic.

To ensure that the only allowed traffic source is CloudFront IP ranges, we need to specify these IP ranges in the firewall rules, and specify “Allow” as an action. However, CloudFront IP ranges change constantly and it would be both cumbersome and unsafe to try updating firewall rules manually as it is prone to human mistake.

For that reason, this artifact focuses on creating automated network firewall rules utilizing the various AWS services such as Simple Notification Service, Parameter Store, and Lambda. 



## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

