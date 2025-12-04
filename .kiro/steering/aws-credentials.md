# AWS Credentials Management

When AWS CLI commands fail due to missing credentials:
- Prompt the user to provide AWS credentials instead of opening new terminals
- Suggest using existing environment variables or AWS profile
- Ask user to run AWS configuration commands in their current terminal
- Remind user that new terminal sessions lose existing credentials
