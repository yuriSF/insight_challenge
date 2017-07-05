import unittest
import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from social_network import *

class SocialNetworkTests(unittest.TestCase):
    def testInitialization(self):
        network = create_social_network_form_batch_file('./test-data/sample-smoke-test.log')
        self.assertEquals(2, network.friendsSearchDegree)
        self.assertEquals(50, network.consecutivePurchases)

    def testBeFriend(self):
        network = create_social_network_form_batch_file('./test-data/sample-befriend.log')
        self.assertEquals(2, len(network.users))
        self.assertEquals(1, len(network.users[10].friends))
        self.assertEquals(1, len(network.users[20].friends))
        self.assertEquals(20, next(iter(network.users[10].friends)).id)
        self.assertEquals(10, next(iter(network.users[20].friends)).id)

    def testUnfriend(self):
        network = create_social_network_form_batch_file('./test-data/sample-befriend.log')
        process_log('./test-data/sample-unfriend.log', network)
        self.assertEquals(2, len(network.users))
        self.assertEquals(0, len(network.users[10].friends))
        self.assertEquals(0, len(network.users[20].friends))

    def testPurchaseSortingByTimestamp(self):
        network = SocialNetwork()
        network.purchaseTracker.register_purchase(Purchase(None, 0, '1'))
        network.purchaseTracker.register_purchase(Purchase(None, 0, '5'))
        network.purchaseTracker.register_purchase(Purchase(None, 0, '2'))
        network.purchaseTracker.register_purchase(Purchase(None, 0, '4'))
        network.purchaseTracker.register_purchase(Purchase(None, 0, '3'))
        self.assertListEqual(['1', '2', '3', '4', '5'], map(lambda p: p.timestamp, network.purchaseTracker.purchases))

    def testPurchaseSortingByTimestampSameItems(self):
        network = SocialNetwork()
        network.purchaseTracker.register_purchase(Purchase(None, 0, '1'))
        network.purchaseTracker.register_purchase(Purchase(None, 0, '2'))
        network.purchaseTracker.register_purchase(Purchase(None, 2, '2'))
        self.assertListEqual(['1', '2', '2'], map(lambda p: p.timestamp, network.purchaseTracker.purchases))
        self.assertEqual(2, network.purchaseTracker.purchases[-1].amount)

        network = SocialNetwork()
        network.purchaseTracker.register_purchase(Purchase(None, 0, '1'))
        network.purchaseTracker.register_purchase(Purchase(None, 0, '2'))
        network.purchaseTracker.register_purchase(Purchase(None, 2, '1'))
        self.assertListEqual(['1', '1', '2'], map(lambda p: p.timestamp, network.purchaseTracker.purchases))
        self.assertEqual(2, network.purchaseTracker.purchases[1].amount)

        network = SocialNetwork()
        network.purchaseTracker.register_purchase(Purchase(None, 0, '1'))
        network.purchaseTracker.register_purchase(Purchase(None, 0, '2'))
        network.purchaseTracker.register_purchase(Purchase(None, 0, '3'))
        self.assertListEqual(['1', '2', '3'], map(lambda p: p.timestamp, network.purchaseTracker.purchases), )

    def testPurchaseFetching(self):
        network = create_social_network_form_batch_file('./test-data/sample-fetch.log')
        network.consecutivePurchases = 50
        for_user = network.lookup_user(999)
        purchases = network.fetch_user_network_purchases(for_user)
        self.assertListEqual([1, 2, 3, 4, 5, 6, 7], map(lambda p: int(p.amount), purchases), )

        network.consecutivePurchases = 2
        purchases = network.fetch_user_network_purchases(for_user)
        self.assertListEqual([1, 2], map(lambda p: int(p.amount), purchases))

    def testFetchUserSocialNetwork(self):
        network = create_social_network_form_batch_file('./test-data/sample-user-social-network.log')
        friends = network.fetch_user_social_network(network.lookup_user(1))
        self.assertListEqual([2, 3, 4], asIds(friends))

        network.friendsSearchDepth = 2
        friends = network.fetch_user_social_network(network.lookup_user(1))
        self.assertListEqual([2, 3, 4, 5, 6], asIds(friends))

        network.friendsSearchDepth = 3
        friends = network.fetch_user_social_network(network.lookup_user(1))
        self.assertListEqual([2, 3, 4, 5, 6, 7], asIds(friends))

        network.friendsSearchDepth = 1
        friends = network.fetch_user_social_network(network.lookup_user(2))
        self.assertListEqual([1], asIds(friends))

        network.friendsSearchDepth = 2
        friends = network.fetch_user_social_network(network.lookup_user(2))
        self.assertListEqual([1, 3, 4], asIds(friends))

    def testStandardDeviation(self):
        network = create_social_network_form_batch_file('./test-data/sample-standard-deviation.log')
        purchases = network.fetch_user_network_purchases(network.lookup_user(1))
        data = list(map(lambda p: p.amount, purchases))
        result, mean, sd, anomalous_amount = SocialNetwork.anomalous_analysis(1000, data)
        self.assertAlmostEquals(8.6, anomalous_amount, places=1)
        self.assertAlmostEquals(1.87, sd, places=2)

def asIds(users):
    ids = list(map(lambda u: u.id, users))
    ids.sort()
    return ids


def main():
    unittest.main()


if __name__ == '__main__':
    main()

