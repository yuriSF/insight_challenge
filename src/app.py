from social_network import *

network = SocialNetwork()
process_log_quietly('log_input/batch_log.json', network)
process_log('log_input/stream_log.json', network)
