from iam import create_all_iams, destroy_all_iams
from lambdas import create_all_lambdas, destroy_all_lambdas
from step_functions import create_all_states, delete_step_function
from sns import create_all_sns, delete_sns_topic
from sqs import create_all_sqs, delete_sqs_queue
from dynamodb import create_all_dynamodbs, delete_dynamodb_table
from misc import load_from_yaml

## ============================================================================

CONFIG_PATH = 'service_resources.yml'
CONFIG = load_from_yaml(CONFIG_PATH)

def create_all(lambda_role_name, step_function_role_name):
    create_all_iams(lambda_role_name, step_function_role_name)
    create_all_lambdas()
    create_all_sns()
    create_all_sqs()
    create_all_states()
    create_all_dynamodbs()

def destroy_all():
    destroy_all_iams()
    destroy_all_lambdas()

    topic_arn = CONFIG['sns']['topic_arn']
    delete_sns_topic(topic_arn)

    queue_url = CONFIG['sqs']['queue_url']
    delete_sqs_queue(queue_url)

    state_machine_arn = CONFIG['step_function']['state_machine_arn']
    delete_step_function(state_machine_arn)

    user_table_name = 'userTable'
    book_table_name = 'bookTable'
    delete_dynamodb_table(user_table_name)
    delete_dynamodb_table(book_table_name)





lambda_role_name = 'LambdaExecutionRole'
step_function_role_name = 'StepFunctionsExecutionRole'
# create_all(lambda_role_name, step_function_role_name)
destroy_all()