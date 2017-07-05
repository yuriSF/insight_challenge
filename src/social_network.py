import numpy as n
import json
import traceback
import bisect
import datetime

ANOMALOUS_LOG_FILE = 'log_output/flagged_purchases.log'


class SocialNetwork(object):
    def __init__(self):
        self.friendsSearchDepth = 1  # D
        self.consecutivePurchases = 50  # T
        self.analysisEnabled = True
        self.users = {}
        self.purchaseTracker = PurchaseTracker()

    def lookup_user(self, user_id):
        user = self.users.get(user_id, None)
        if user is None:
            user = User(user_id)
            self.users[user_id] = user
        return user

    def add_friends(self, id1, id2):
        user1 = self.lookup_user(id1)
        user2 = self.lookup_user(id2)
        user1.friends.add(user2)
        user2.friends.add(user1)

    def unfriend(self, id1, id2):
        user1 = self.lookup_user(id1)
        user2 = self.lookup_user(id2)
        user1.friends.discard(user2)
        user2.friends.discard(user1)

    def on_purchase(self, user_id, amount, timestamp):
        user = self.lookup_user(user_id)
        purchase = Purchase(user, amount, timestamp)
        self.purchaseTracker.register_purchase(purchase)

        if self.analysisEnabled:
            purchases = self.fetch_user_network_purchases(user)
            data = list(map(lambda p: p.amount, purchases))
            is_anomalous, mean, sd, anomalous_amount = SocialNetwork.anomalous_analysis(amount, data)
            if is_anomalous:
                SocialNetwork.on_anomolous_purchase(user, purchase, mean, sd)

    def fetch_user_network_purchases(self, user):
        result = []
        network = self.fetch_user_social_network(user)
        for p in self.purchaseTracker.purchases:
            if p.user in network:
                result.append(p)
                if len(result) >= self.consecutivePurchases:
                    break
        return result

    @staticmethod
    def anomalous_analysis(amount, data):
        if len(data) < 2:
            return False, None, None, None

        mean = n.mean(data)
        stand_dev = n.std(data)  # standard deviation
        anomalous_amount = mean + (3 * stand_dev)
        return amount > anomalous_amount, mean, stand_dev, anomalous_amount

    @staticmethod
    def on_anomolous_purchase(user, purchase, mean, sd):
        entry = {
            'event_type': 'purchase',
            'id': user.id,
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'mean': round(mean, 2),
            'sd': round(sd, 2)
        }
        print('writing log entry: ')
        print(entry)
        with open(ANOMALOUS_LOG_FILE, "a") as f:
            json.dump(entry, f)
            f.write('\n')

    def fetch_user_social_network(self, user):
        result = set()
        result.add(user)
        self.collect_friends_impl(user.friends, 1, result)
        result.discard(user)
        return result

    def collect_friends_impl(self, friends, depth, out):
        for friend in friends:
            if friend in out:
                continue
            out.add(friend)
            if depth < self.friendsSearchDepth:
                self.collect_friends_impl(friend.friends, depth + 1, out)

    def dispatch_event(self, event):
        event_type = event['event_type']
        if event_type == 'purchase':
            self.on_purchase(event['id'], event['amount'], event['timestamp'])
        elif event_type == 'befriend':
            self.add_friends(event['id1'], event['id2'])
        elif event_type == 'unfriend':
            self.unfriend(event['id1'], event['id2'])


class User:
    def __init__(self, used_id):
        self.id = used_id
        self.friends = set()


class Purchase:
    def __init__(self, user, amount, timestamp):
        self.user = user
        self.amount = amount
        self.timestamp = timestamp


class PurchaseTracker:
    def __init__(self):
        self.purchases = []
        self.purchases_timestamps = []

    def add(self, purchase):
        self.purchases.append(purchase)
        self.purchases_timestamps.append(purchase.timestamp)

    def insert(self, index, purchase):
        self.purchases.insert(index, purchase)
        self.purchases_timestamps.insert(index, purchase.timestamp)

    def register_purchase(self, purchase):
        size = len(self.purchases)
        if size == 0:
            self.add(purchase)
            return
        # most common case
        last = self.purchases[len(self.purchases) - 1]
        if purchase.timestamp >= last.timestamp:
            self.add(purchase)
        else:
            index = bisect.bisect_right(self.purchases_timestamps, purchase.timestamp)
            self.insert(index, purchase)


def create_social_network_form_batch_file(batch_file):
    network = SocialNetwork()
    process_log(batch_file, network)
    return network


def process_log_quietly(log_file, network):
    state = network.analysisEnabled
    network.analysisEnabled = False
    process_log(log_file, network)
    network.analysisEnabled = state


def process_log(log_file, network):
    with open(log_file) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                if 'event_type' in entry:
                    typify(entry)
                    network.dispatch_event(entry)
                elif 'D' in entry and 'T' in entry:
                    d = int(entry['D'])
                    t = int(entry['T'])
                    if d >= 1:
                        network.friendsSearchDegree = d
                    if t >= 2:
                        network.consecutivePurchases = t
            except Exception:
                print('unable to process:')
                print(line)
                traceback.print_exc()


TYPES_TABLE = {
    'amount': float,
    'id': int,
    'id1': int,
    'id2': int
}


def typify(entry):
    for field in TYPES_TABLE:
        coercer = TYPES_TABLE[field]
        if field in entry:
            entry[field] = coercer(entry[field])
