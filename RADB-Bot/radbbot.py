import os
import time
import re
import requests
from slackclient import SlackClient

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# radbbot's user ID in Slack: value is assigned after the bot starts up
radbbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

# commands
BLANCO_COMMAND = "blanco"
RADB_STATUS_COMMAND = "status"
HELP_COMMAND = "help"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == radbbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second one contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # default response is help text for the user
    response = ["Not sure what you mean. Try *{}*.".format(HELP_COMMAND)]

    if command.startswith (HELP_COMMAND):
        del response[:]
        response.append("These are the commands you can ask me to respond:\n*{}, {}*".format(BLANCO_COMMAND, RADB_STATUS_COMMAND))

    if command.startswith (BLANCO_COMMAND):
        del response[:]
        response.append("I'm a fucking nigga!!!")

    if command.startswith (RADB_STATUS_COMMAND):
        del response[:]
        api_resp = requests.get(url="https://redis-test-223116.appspot.com/health-check")
        data = api_resp.json()

        temp = "Here you are the API status report: \n\n" +\
                "Riot webpage:  *{}* \n".format(":white_check_mark:" if data["riotWebpageIsUp"] else ":warning:") +\
                "ChampionGG Status:  *{}* \n".format(":white_check_mark:" if data["championGGIsUp"] else ":warning:") +\
                "Google datastore:  *{}* \n".format(":white_check_mark:" if data["datastoreIsUp"] else ":warning:")\

        if any(data["afectedRiotEndpoints"]):
            temp = temp +"\nHere is the list of affected Riot endpoints: \n\n"
            for keyEP, valueEP in data["afectedRiotEndpoints"].iteritems():
                temp = temp + ":warning: *{}* in: ".format(keyEP)
                for keyR, valueR in valueEP.iteritems():
                    temp = temp + "{} ".format(keyR)
                temp = temp + "\n"
            temp = temp +"\n The rest of the endpoints are OK :white_check_mark:.\n"
        else:
            temp = temp + "All Riot endpoints: :white_check_mark:"

        response.append(temp)
    
    # sends the response back to the channel
    for message in response:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=message
        )
        time.sleep(RTM_READ_DELAY)

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("RADB Bot connected and running!")
        # Read bot's user ID by calling Web API method 'auth.test'
        radbbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")