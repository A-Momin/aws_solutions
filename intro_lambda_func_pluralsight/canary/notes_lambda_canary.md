## AWS Development using AWS Console

### Create a Lambda Function

0. LambdaConsole => Click: CreateFunction => Select: Use-a-Blueprint => Focus: BlueprintName => Search: 'Schedule a periodic check'
1. FunctionName => Name: lambda_canary
1. ExecutionRole => Select: 'Create a new role with basic Lambda permissions'

### EventBridge (CloudWatch Events) trigger

0. EvnetBridgeConsole => Click: Rule => Select: 'Create a new rule'
1. RuleName => Name: canary
2. Description => Name: Five Minutes Rule
3. RuleType => Select: 'Schedule expression'
4. ScheduleExpression => Name: 'rate(5 minutes)'

### Define Environment Variables for Lambda function

0. Key => Name: site
1. Value => Name: http://httpbin.org/
2. Key => Name: expect
3. Value => Name: httpbin

---

---

## AWS Development using AWS CLI
