'''
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
'''


import sys
import irc.bot
import requests
from time import sleep
import random
from threading import Thread
import json
#import urllib2


class TwitchBot(irc.bot.SingleServerIRCBot):
    entries = None
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        self.entries = list()

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)

    # def choose(self):
    #     c = self.connection
    #     if not self.entries:
    #         c.privmsg(self.channel, 'No entries received. Trying again')
    #         return False
    #     else:
    #         choice = random.choice(self.entries)
    #         c.privmsg(self.channel, '/host ' + choice)
    #         c.privmsg(self.channel, 'Now hosting '+ choice)
    #         del self.entries[:]
    #         self.entries = list()
    #         return True

    def on_welcome(self, c, e):
        print('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)
        c.privmsg(self.channel, 'Starting ZachBot...')
        #   Below code used for multithreading for hosting input
        #c.privmsg(self.channel, 'Input !hostme NOW for a chance to be hosted!')
        # try:
        #     t1 = Thread(target=self.run).start()
        # except (KeyboardInterrupt, SystemExit):
        #     print('\nKeyboard Interrupt, exiting threading')
        #     t1.join()

    def get_JSON(self, user_id):
        url = 'https://api.twitch.tv/helix/users?login=' + user_id
        headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        print(r)
        return r

    # def run(self):
    #     is_streaming = False
    #     are_entries = False
    #     while True:
    #         if is_streaming == True:
    #             is_streaming = self.cur_streaming()
    #         else:
    #             is_streaming = self.timer_get()
    #             are_entries = self.choose()
    #             if are_entries == True:
    #                 is_streaming = self.timer_hosting()
    #
    #
    # def cur_streaming(self):
    #     streaming = True
    #     while streaming == True:
    #         url = 'https://api.twitch.tv/kraken/streams/' + self.channel_id
    #         headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
    #         try:
    #             r = requests.get(url, headers=headers).json()
    #         except ValueError:
    #             continue
    #         except requests.exceptions.ConnectionError:
    #             continue
    #         if not r['stream']:
    #             streaming = False
    #         sleep(1)
    #     return False
    #     #self.timer_get()
    #
    # def timer_get(self):
    #     c = self.connection
    #     c.privmsg(self.channel, 'Input !hostme NOW for a chance to be hosted!')
    #     time = 60 * 2
    #     for i in range(time):
    #         url = 'https://api.twitch.tv/kraken/streams/' + self.channel_id
    #         headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
    #         try:
    #             r = requests.get(url, headers=headers).json()
    #         except ValueError:
    #             continue
    #         except requests.exceptions.ConnectionError:
    #             continue
    #         try:
    #             if r['stream']:
    #                 return True
    #         except KeyError:
    #             continue
    #         sleep(1)
    #     return False
    #
    # def timer_hosting(self):
    #     c = self.connection
    #     time = 60 * 20
    #     for i in range(time):
    #         url = 'https://api.twitch.tv/kraken/streams/' + self.channel_id
    #         headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
    #         try:
    #             r = requests.get(url, headers=headers).json()
    #         except ValueError:
    #             continue
    #         except requests.exceptions.ConnectionError:
    #             continue
    #         try:
    #             if r['stream']:
    #                 return True
    #         except KeyError:
    #             continue
    #         sleep(1)
    #     c.privmsg(self.channel, '/unhost')
    #     return False

    def on_pubmsg(self, c, e):
        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
  #          print e.arguments[0][0]
 #           print e.arguments[0]
            user_name =  e.source.split('!')[0]
#            print e
            cmd = e.arguments[0].split(' ')[0][1:]
            cmd = cmd.lower()
            #print 'Received command: ' + cmd
            self.do_command(e, cmd, user_name)
        return

    def do_command(self, e, cmd, user_name):
        c = self.connection
        # Poll the API to get current game.
        if cmd == "game":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] + ' is currently playing: ' + r['game'])

        # Poll the API the get the current status of the stream
        elif cmd == "title":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] + ' channel title is currently: ' + r['status'])

        elif cmd == "hello":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, 'Hello, ' + user_name)

        elif cmd == "psn":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, 'PSN: Internal-Scream')

        elif cmd == "switch":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, 'Switch Friend Code: SW-1828-2068-1404')

        elif cmd == "r3poopooqt" or cmd == "r3trace":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, 'BEEP BOOP I\'M A CUTIE')  # Thank you Guaconmysock

        elif cmd == "followage" or cmd == "followtime":
            #r_to = self.get_JSON(self.channel_id)
            #print(r_to)

            url = 'https://api.twitch.tv/helix/users?login=' + user_name
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()

            #print(r)
            #print(r['data'][0]['id'])
            from_id = r['data'][0]['id']
            #id_url = 'https://api.twitch.tv/helix/users/follows?from_id=' + user_id
            #print(id_url)
            # https://api.twitch.tv/helix/users/follows?first=1&from_id=1336&to_id=1337
            if from_id == self.channel_id:
                c.privmsg(self.channel, 'You can\'t follow yourself, ' + user_name + '!')
            else:
                id_url = 'https://api.twitch.tv/helix/users/follows?first=1&from_id=' + from_id + '&to_id=' + self.channel_id
                headers_2 = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
                r_2 = requests.get(id_url, headers=headers_2).json()
                #print(r_2)
                try:
                    follow_date = r_2['data'][0]['followed_at']
                    follow_date = follow_date.replace('T', ' ')  # need space
                    follow_date = follow_date.replace('Z', '')  # do not need space
                    from datetime import datetime
                    # e.g. 2014-06-07T04:24:32Z
                    # "%Y-%m-%d %H:%M:%S
                    # print(start)
                    to_start = datetime.strptime(follow_date, '%Y-%m-%d %H:%M:%S')
                    str_len = datetime.utcnow() - to_start
                    # print(str_len)
                    str_len = str(str_len)
                    c.privmsg(self.channel, user_name + ' has been following ' + self.channel + ' ' + str_len)

                except KeyError:
                    c.privmsg(self.channel, user_name + ' is not following ' + self.channel)
                except IndexError:
                    c.privmsg(self.channel, user_name + ' is not following ' + self.channel)


            #c.privmsg(self.channel, r)

        elif cmd == "commands":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, '!hello, !game, !title, !psn, !switch, !status, !lurk, !platform, !delay, !rez, !uptime')


        # elif cmd == "uptime":
        #     url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
        #     headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        #     r = requests.get(url, headers=headers).json()
        #     print(r)


        # elif cmd == "hostme":
        #     channel = self.channel.split('#')[1]
        #     #print user_name
        #     if user_name == channel:
        #         c.privmsg(self.channel, 'You can\'t host yourself!')
        #     else:
        #         url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
        #         headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        #         try:
        #             r = requests.get(url, headers=headers).json()
        #             self.entries.append(user_name)
        #             c.privmsg(self.channel, user_name + ' has been added to the host list')
        #         except ValueError:
        #             c.privmsg(self.channel, user_name + ', a problem has occurred. Please type !hostme again.')
        #         #c.privmsg(self.channel, '/host ' + user_name)
        #
        #         #print self.entries

        # elif cmd == "hostlist":
        #     url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id + '/autohost/list'
        #     headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        #     r = requests.get(url, headers=headers).json()
        #     print r

        elif cmd == "status":
            channel = self.channel.split('#')[1]
            #twitch_api_stream_url = "https://api.twitch.tv/kraken/streams/" + channel + "?client_id=" + self.client_id
            #streamer_html = requests.get(twitch_api_stream_url)
            #streamer = json.loads(streamer_html.content)
            #print twitch_api_stream_url
            #print streamer_html
            #print streamer
            #if not streamer['stream_type']:
            #    c.privmsg(self.channel, 'Not Live')
            #else:
            #    c.privmsg(self.channel, streamer['stream_type'])
            #c.privmsg(self.channel, streamer["stream"])

            url = 'https://api.twitch.tv/kraken/streams/'+self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}

            r = requests.get(url, headers=headers).json()
            #print url
            #print r
            if not r['stream']:
                c.privmsg(self.channel, 'Not Live')
            else:
                c.privmsg(self.channel, 'Live')



        elif cmd == "express":
            c.privmsg(self.channel, 'https://express.google.com/invite/3UJ5VF2M3')


        elif cmd == "lurk" or cmd == "lurking":
            c.privmsg(self.channel, user_name + ", thanks for lurking!")

        elif cmd == "platform":
            url = 'https://api.twitch.tv/kraken/streams/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, "System: "+r['stream']['broadcast_platform'])

        elif cmd == "delay":
            url = 'https://api.twitch.tv/kraken/streams/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, "Delay: "+str(r['stream']['delay']))

        elif cmd == "rez":
            url = 'https://api.twitch.tv/kraken/streams/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, "Resolution: "+str(r['stream']['video_height'])+"p")

        elif cmd == "uptime":
            url = 'https://api.twitch.tv/kraken/streams/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            #print(r)
            try:

                start = r['stream']['created_at']
                #to_split = start.split('T')
                #date = to_split[0]
                #time = to_split[1]
                #for letter in "Z":
                #time = time.replace('Z', '')
                start = start.replace('T', ' ')#need space
                start = start.replace('Z', '')#do not need space
                from datetime import datetime
                #e.g. 2014-06-07T04:24:32Z
                #"%Y-%m-%d %H:%M:%S
                #print(start)
                to_start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                str_len = datetime.utcnow() - to_start
                #print(str_len)
                str_len = str(str_len)
                c.privmsg(self.channel, str_len)

            except Exception as e:
                temp_msg = "Not Live"
                c.privmsg(self.channel, temp_msg)


        # The command was not recognized
        else:
            c.privmsg(self.channel, "Did not understand command: " + cmd)






def main():
    if len(sys.argv) != 5:
        print("Usage: twitchbot <username> <client id> <token> <channel>")
        sys.exit(1)

    username  = sys.argv[1]
    client_id = sys.argv[2]
    token     = sys.argv[3]
    channel   = sys.argv[4]

    bot = TwitchBot(username, client_id, token, channel)
    bot.start()

if __name__ == "__main__":
    main()

