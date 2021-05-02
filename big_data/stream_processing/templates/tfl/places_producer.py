from transportforlondon.places import Places
import argparse
import logging
import pprint
import sys
import os

# Auxiliary functions
#

# Action functions for the functions calling the REST API
#
def kafka_producer_decorator(broker, topic):
  ''' Decorator (function that takes another function) to create functions ready
      to publish messages to a specific topic and Kafka broker.

            Parameters:
                    broker (string): host:port of the Kafka broker
                    topic (string): topic name where the a message is going to be published

            Returns:
                    A function ready to publish messages to a specific topic and Kafka broker.
  '''

  def kafka_producer_action(content):
    ''' Function with the logic to publish messages into a Kafka topic. THIS IS THE FUNCTION
        WHERE YOU HAVE TO WORK ON.

            Parameters:
                    content (list): List of dictionaries (JSON) documents; if only one JSON
                                    document is returned from the web service, the list will
                                    only have 1 element.

            Returns:
                    This function doesn't return anything.
    '''

    if isinstance(content, list):
      for item in content:
        # add your logic to publish into the topic here
        #
        pass
    else:
      print("No contents received. Nothing will be published into the topic.")
      logging.info("No contents received. Nothing will be published into the topic.")

  return kafka_producer_action

def pprint_action(content):
  ''' Function displaying the content on the standard output (screen). Useful for debugging
      purposes.

          Parameters:
                  content (list): List of dictionaries (JSON) documents; if only one JSON
                                  document is returned from the web service, the list will
                                  only have 1 element.

          Returns:
                  This function doesn't return anything.
  '''

  pp = pprint.PrettyPrinter(indent=2)
  pp.pprint(content)

# Decorators on functions calling the REST API
#
def info_charge_connectors_decorator(action_func):
  ''' Decorator (function that takes another function) to create a function retrieving
      information of bike stations and executing the 'action_func' function on the 
      results.

            Parameters:
                    action_func (function): the function that will be applied on the results.

            Returns:
                    A function ready to retrieve information of bike stations and executing the
                    'action_func' function on the results.
  '''

  def info_charge_connectors(places_service):
    ''' Function retrieving information of charge connectors and executing the 'action_func' 
        function on the results.

              Parameters:
                      places_service: instance leveraging the Place API.

              Returns:
                      Nothing
    '''

    info_charge_connectors = places_service.info_charge_connectors()

    if info_charge_connectors!=None:
      action_func(info_charge_connectors)
    else:
      print("The Place API didn't return any data.")

  return info_charge_connectors

def info_charge_stations_decorator(action_func):
  ''' Decorator (function that takes another function) to create a function retrieving
      information of bike stations and executing the 'action_func' function on the 
      results.

            Parameters:
                    action_func (function): the function that will be applied on the results.

            Returns:
                    A function ready to retrieve information of bike stations and executing the
                    'action_func' function on the results.
  '''

  def info_charge_stations(places_service):
    ''' Function retrieving the information of charge stations and executing the 'action_func' 
        function on the results.

              Parameters:
                      places_service: instance leveraging the Place API.

              Returns:
                      Nothing
    '''

    info_charge_stations = places_service.info_charge_stations()

    if info_charge_stations!=None:
      action_func(info_charge_stations)
    else:
      print("The Place API didn't return any data.")

  return info_charge_stations

def build_kafka_producer(broker, topic):
  ''' This function creates a function ready to produce messages into Kafka.

            Parameters:
                    broker (string): host:port of the Kafka broker
                    topic (string): topic name where the a message is going to be published

            Returns:
                    A function ready to produce messages into a Kafka topic or None if no broker nor topic
                    are not provided.
  '''
  if broker!=None and topic!=None:
    logging.debug("Application executed as a Kafka producer")
    return kafka_producer_decorator(broker, topic)
  else:
    logging.debug("Application not executed as a Kafka producer")

  return None


if __name__ == "__main__":
  # Setting up debuging level and debug file with environment variables
  #
  debug_level = os.environ.get('MOBILITYLABS_DEBUGLEVEL',logging.WARN)
  debug_file = os.environ.get('MOBILITYLABS_DEBUGFILE')

  if debug_file==None:
    logging.basicConfig(level=debug_level)
  else:
    logging.basicConfig(filename=debug_file, filemode='w', level=debug_level)

  parser = argparse.ArgumentParser()
  parser.add_argument("action", choices=['info_charge_connectors', 'info_charge_stations'],
                      help="what is going to be requested to the Place API")
  parser.add_argument("-b", "--broker",
                      help="server:port of the Kafka broker where messages will be published")
  parser.add_argument("-t", "--topic",
                      help="topic where messages will be published")
  args = parser.parse_args()

  places_service = Places()
  action_function = build_kafka_producer(args.broker, args.topic)
  if action_function==None:
    action_function = pprint_action;

  if args.action == "info_charge_connectors":
    logging.debug("asking for info of all charge connectors")
    info_charge_connectors = info_charge_connectors_decorator(action_function)
    info_charge_connectors(places_service)
  elif args.action == "info_charge_stations":
    logging.debug("asking for info of all charge stations")
    info_charge_stations = info_charge_stations_decorator(action_function)
    info_charge_stations(places_service)
