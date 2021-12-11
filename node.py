#! /usr/bin/python3

import sys
import random

from world import world, log

if __name__ == '__main__':

    log(f'Hello from node{world.current_node}')
    log(f'I\'m connected to nodes {world.neighbors}')
    log(f'I have edges {world.edges}')

    net_size = world._world_map.number_of_nodes()
    node_id = random.choice(list(range(net_size)))
    world.node_id = node_id
    log(f'I selected {node_id} as my id')

    for node in world.neighbors:
        if node != world.current_node:
            world.send_message(node, f'0,{node_id},0')
    try:
        world.listen()
    except KeyboardInterrupt:
        log("received keyboard interrupt")
        sys.exit(0)
