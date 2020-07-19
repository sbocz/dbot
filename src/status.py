from discord import ActivityType
from discord import Activity

# Status constants
PLAYING_ACTIVITY = 'PLAYING'
LISTENING_ACTIVITY = 'LISTENING'
WATCHING_ACTIVITY = 'WATCHING'
STREAMING_ACTIVITY = 'STREAMING'


class Status:
    '''Discord status data object'''
    text: str
    activity_type: ActivityType
    activity: Activity

    def __init__(self, text: str, activity_type: ActivityType):
        self.activity_type = activity_type
        self.text = text
        self.activity = Activity(name=self.text, type=self.activity_type)

    @staticmethod
    def from_dict(dictionary):
        '''Constructs a status from a dictionary'''
        switcher = {
            WATCHING_ACTIVITY: ActivityType.watching,
            LISTENING_ACTIVITY: ActivityType.listening,
            PLAYING_ACTIVITY: ActivityType.playing,
            STREAMING_ACTIVITY: ActivityType.streaming
        }
        return Status(str(dictionary['text']), switcher.get(dictionary['activity_type'], ActivityType.playing))
