import click
import boto3
import random

from time import sleep
from tqdm import tqdm

running = True

@click.command()
@click.option('--amount', default=1, help="NONE")
@click.option('--time', default=30, help="NONE")
@click.option('--file', help="NONE")

def start(amount, time):

  #signal.signal(signal.SIGTERM, handler)
  #signal.signal(signal.SIGHUP, handler)

  instances = []

  """
  while running:
    instances.append(instance(amount))

    random_time = random.randint(1, time)
    time.sleep(random_time)

  for ec2 in instances:
    ec2.terminate()
    ec2.wait_until_terminated()
    click.echo(f"Instance is {ec2.state['Name']}.")
  """

  try:

    while running:
      new = list(instance(amount))
      instances.extend(new)
      #[wait(ec2) for ec2 in new]

      for ec2 in tqdm(new):
        wait(ec2)

      random_time = random.randint(1, time)
      sleep(random_time)
    
  except KeyboardInterrupt:
    pass

  for ec2 in tqdm(instances):

    click.echo(f"Waiting for instance to be up - {ec2.instance_id}... ")
    ec2.wait_until_running()
    click.echo(f"Terminating instance - {ec2.instance_id}... ")
    ec2.terminate()

  for ec2 in tqdm(instances):
    
    click.echo(f"Waiting for instance to be terminated - {ec2.instance_id}... ")
    ec2.wait_until_terminated()
    click.echo(f"Instance {ec2.instance_id} is {ec2.state['Name']}.")


#def handler(signum, frame):
#  running = False

def instance(amount):

  number = random.randint(1, amount)

  click.echo(f"Starting {number} Instances.")

  for instance in range(number):

    ec2_client = boto3.client('ec2')
    ec2_image = boto3.resource('ec2')

    images = ec2_client.describe_images(
      Filters=[
            {
                'Name': 'name',
                'Values': [
                    'amzn2-ami-hvm*',
                ]
            },
            {
                'Name': 'owner-alias',
                'Values': [
                    'amazon',
                ]
            },
        ],
    )

    AMI = ec2_image.Image(images['Images'][0]['ImageId'])

    if AMI.state == "available":

      click.echo("ImageID: " + str(AMI.image_id))

      instance = ec2_client.run_instances(
        ImageId=AMI.image_id,
        InstanceType='t2.nano',
        MaxCount=1,
        MinCount=1,
        DryRun=False,
        #Ipv6AddressCount=1
        user_data=user_data_script
      )

      ec2_instance = boto3.resource('ec2')
      ec2 = ec2_instance.Instance(instance['Instances'][0]['InstanceId'])

      click.echo(f"Starting Instance: {(ec2.instance_id)}...")
 
      yield ec2

      #ec2.terminate()
      #ec2.wait_until_terminated()
      #click.echo(f"Instance is {ec2.state['Name']}.")

    else: 
      click.echo("The AMI was not available!")

def wait(ec2):
  click.echo(f"Waiting for Instance {ec2.instance_id}.")
  ec2.wait_until_running()
  click.echo(f"Instance {ec2.instance_id} is {ec2.state['Name']}.")

  return ec2

if __name__ == '__main__':
  start()