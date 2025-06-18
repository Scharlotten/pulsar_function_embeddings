# Apache Pulsar Function Setup Guide

## Overview

Apache Pulsar is a distributed messaging and streaming platform that provides serverless compute capabilities through Pulsar Functions. Functions are lightweight compute processes that consume messages from input topics, apply user-defined processing logic, and optionally produce results to output topics.

## Key Benefits of Pulsar Functions

- **Serverless Computing**: No need to manage infrastructure
- **Language Support**: Java, Python, and Go
- **Automatic Scaling**: Functions scale based on message throughput
- **Fault Tolerance**: Built-in error handling and retry mechanisms
- **State Management**: Stateful processing capabilities

## Prerequisites

- Apache Pulsar cluster running
- Python environment with required dependencies
- Access to Pulsar admin tools

## Building the Code

Install dependencies with platform-specific binaries:

```bash
pip download -d ./deps -r requirements.txt --only-binary=:all: --platform manylinux2014_x86_64
```

## Setup Steps

### 1. Create the Tenant

Tenants provide multi-tenancy support and resource isolation:

```bash
bin/pulsar-admin tenants create apache
```

### 2. Create the Namespaces

Namespaces group related topics and provide policy boundaries:

```bash
bin/pulsar-admin namespaces create apache/pulsar
```

### 3. Create the Source Topic

Create a partitioned topic for better throughput and parallel processing:

```bash
bin/pulsar-admin topics create-partitioned-topic apache/pulsar/wiki-topic -p 3
```

**Note**: You can rename topics, but ensure you update the corresponding `config.yaml` file accordingly.

### 4. Set Retention Policy

Configure message retention to control storage usage:

```bash
bin/pulsar-admin namespaces set-retention my-tenant/my-ns --size 1G --time 3h
```

This sets retention to 1GB of storage or 3 hours, whichever limit is reached first.

### 5. Create the Function

Deploy your function with resource specifications:

```bash
bin/pulsar-admin functions create \
  --function-config-file=~/CodeProjects/pulsar-producer/create-config.yaml \
  --cpu=0.2 \
  --ram=400000000
```

### 6. Update the Function

If you need to modify an existing function:

```bash
bin/pulsar-admin functions update \
  --function-config-file=~/CodeProjects/pulsar-producer/create-config.yaml \
  --cpu=0.2 \
  --ram=400000000
```

## Additional Configuration Options

### Resource Management

- **CPU**: Specify CPU cores (e.g., 0.2 = 20% of one core)
- **RAM**: Memory allocation in bytes (400000000 = ~400MB)
- **Disk**: Storage allocation for stateful functions

### Function Configuration File

The `config.yaml` file typically includes:

- Input/output topics
- Processing logic location
- Serialization/deserialization settings
- Error handling policies
- Parallelism settings

### Monitoring and Management

Use these commands to manage your functions:

```bash
# List all functions
bin/pulsar-admin functions list --tenant apache --namespace pulsar

# Get function status
bin/pulsar-admin functions status --tenant apache --namespace pulsar --name your-function

# View function logs
bin/pulsar-admin functions logs --tenant apache --namespace pulsar --name your-function

# Delete a function
bin/pulsar-admin functions delete --tenant apache --namespace pulsar --name your-function
```

## Best Practices

1. **Resource Allocation**: Start with conservative CPU/RAM settings and scale based on performance metrics
2. **Error Handling**: Implement proper error handling and dead letter topics
3. **Monitoring**: Set up metrics collection and alerting
4. **Testing**: Test functions thoroughly in development environments
5. **Versioning**: Use version control for function configurations and code

## Additional Resources

For comprehensive documentation and examples, visit the official Pulsar Functions guide:
[https://pulsar.apache.org/docs/4.0.x/functions-quickstart/](https://pulsar.apache.org/docs/4.0.x/functions-quickstart/)

## Troubleshooting

Common issues and solutions:

- **Function fails to start**: Check resource limits and configuration syntax
- **Message processing delays**: Consider increasing parallelism or CPU allocation
- **Memory errors**: Increase RAM allocation or optimize function code
- **Topic not found**: Verify topic creation and naming consistency