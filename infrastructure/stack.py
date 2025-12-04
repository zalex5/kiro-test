from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    Duration,
    RemovalPolicy
)
from constructs import Construct

class EventApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = dynamodb.Table(
            self, "EventsTable",
            partition_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        users_table = dynamodb.Table(
            self, "UsersTable",
            partition_key=dynamodb.Attribute(
                name="userId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        registrations_table = dynamodb.Table(
            self, "RegistrationsTable",
            partition_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="userId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        registrations_table.add_global_secondary_index(
            index_name="UserIdIndex",
            partition_key=dynamodb.Attribute(
                name="userId",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            )
        )

        api_lambda = lambda_.Function(
            self, "EventApiFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="app.handler",
            code=lambda_.Code.from_asset("../backend"),
            timeout=Duration.seconds(30),
            environment={
                "TABLE_NAME": table.table_name,
                "USERS_TABLE_NAME": users_table.table_name,
                "REGISTRATIONS_TABLE_NAME": registrations_table.table_name
            }
        )

        table.grant_read_write_data(api_lambda)
        users_table.grant_read_write_data(api_lambda)
        registrations_table.grant_read_write_data(api_lambda)

        api = apigw.LambdaRestApi(
            self, "EventApi",
            handler=api_lambda,
            proxy=True,
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["*"]
            )
        )
