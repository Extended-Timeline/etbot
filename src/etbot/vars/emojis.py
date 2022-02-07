import sys

this = sys.modules[__name__]

yes_vote = None
no_vote = None
abstain_vote = None
recycle = None
ear_with_hearing_aid = None


def initialize_testing_emojis():
    this.yes_vote = "<:Yes:867869297329176587>"
    this.no_vote = "<:No:867869349041799198>"
    this.abstain_vote = "<:Abstain:867869367601070081>"
    this.recycle = "♻"
    this.ear_with_hearing_aid = "🦻"


def initialize_emojis():
    this.yes_vote = "<:Yes:698226023795261451>"
    this.no_vote = "<:No:698226052899799130>"
    this.abstain_vote = "<:Abstain:698226077113516118>"
    this.recycle = "♻"
    this.ear_with_hearing_aid = "🦻"
