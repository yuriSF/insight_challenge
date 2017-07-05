## Approach

The class SocialNetwork encapsulates the graph of all users and stores the history of all purchases. SocialNetwork ensures that all purchases are sorted by timestamp. To search a user's social network, a recursive DFS algorithm is used, limited by parameter D and testing for loops in the graph.

## Running the application

To run the application: execute ./run.sh
To run the tests: cd insight_testsuite and execute ./run_tests.sh

## Dependency

The numpy library is used to calculate Standard Deviation.
