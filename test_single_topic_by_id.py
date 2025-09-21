#

import sys

from helpers import EinkTopic, TEMP_DIR
from gen_slide import run__slide


if __name__ == "__main__":
    if len(sys.argv) != 2 or int(sys.argv[1]) not in [0,1,2,3,4,5]:
        print("Usage:  python3 test_single_topic_by_id.py <topic id, 0 to 5>")
        exit()
    print(sys.argv)
    target_topic = EinkTopic(int(sys.argv[1]))
    print("Target topic: ", target_topic)
    run__slide(target_topic, TEMP_DIR)
