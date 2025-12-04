#!/usr/bin/env python3
import aws_cdk as cdk
from stack import EventApiStack

app = cdk.App()
EventApiStack(app, "EventApiStack")
app.synth()
