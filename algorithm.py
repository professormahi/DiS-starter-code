import sys
import random

from world import log, world


got_msg_from = []
current_wave = world.node_id
round = 0
parent = None
net_size = world._world_map.number_of_nodes()
subtree_size = 0
children = [node for node in world.neighbors if node != world.current_node]
leader_node = None


def decode_le_msg(msg):
    
    m_round, m_id, s_size = msg.split(",")
    m_round = int(m_round)
    m_id = int(m_id)
    s_size = int(s_size)

    return m_round, m_id, s_size


def initialize_a_round(m_round, m_id, src):

    global round, current_wave, parent, subtree_size, children, got_msg_from

    round = m_round
    parent = src
    current_wave = m_id
    got_msg_from = []
    subtree_size = 0

    children = [node for node in world.neighbors if node != world.current_node]
    if parent is not None:
        children.remove(parent)
    log(f'my parent is {parent}, i am in wave {current_wave} and my children are: {children}')
    for node in children:
        world.send_message(node, f'{round},{current_wave},0')


def decide_after_children_responses():

    global round, current_wave, parent, subtree_size, children, got_msg_from, leader_node

    if parent is None and subtree_size+1 == net_size:
        log(f'I am the leader! my name is {world.current_node} and my id is {world.node_id}')
        children = [node for node in world.neighbors if node != world.current_node]
        leader_node = world.current_node
        log(f'I am sending leader: {world.current_node} to my children: {children}')
        log(f'got msg from: {got_msg_from}')
        for node in children:
            world.send_message(node, f'leader:{world.current_node}')
        world.send_message(to=world.current_node, msg='exit')
        
    elif parent is None and subtree_size+1 < net_size:
        round += 1
        node_id = random.choice(list(range(net_size)))
        world.node_id = node_id
        log(f'I selected {node_id} as my id')

        initialize_a_round(round, node_id, None)

    else:
        log(f'my subtree size is: {subtree_size+1} and i send it to {parent}')
        world.send_message(parent, f'{round},{current_wave},{subtree_size+1}')


def process_msg(src, msg):

    global got_msg_from, current_wave, round, parent, subtree_size, children, leader_node

    log(f"message from {src}: {msg}")

    if msg == "exit":
        print(leader_node)
        sys.exit()

    elif 'leader' in msg.split(':'):
        if leader_node is None:
            leader = msg.split(':')[1]
            leader_node = leader
            children = [node for node in world.neighbors if node != world.current_node]
            log(f'I am sending leader: {leader} to my children: {children}')
            log(f'got msg from: {got_msg_from}')
            for node in children:
                world.send_message(node, f'leader:{leader}')
            world.send_message(to=world.current_node, msg='exit')

    else:
        m_round, m_id, s_size = decode_le_msg(msg)

        if (m_round > round) or ((m_round == round) and (m_id > current_wave)):
            log(f'I joined a new wave with round {m_round} and id {m_id} and my parent is: {src}')
            initialize_a_round(m_round, m_id, src)

        elif (m_round == round) and (m_id == current_wave):
            got_msg_from.append(src)
            subtree_size += s_size
            log(f'my parent is: {parent} and i got msg from: {got_msg_from} and my subtreesize is {subtree_size}')

            if set(got_msg_from) == set(children):
                decide_after_children_responses()
