class Node(object):
    def __init__(self, data, prev, next):
        self.data = data
        self.prev = prev
        self.next = next


class DoubleList(object):
    head = None
    tail = None
    length = 0

    def prepend(self, data):
        new_node = Node(data, None, None)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node

        self.length += 1

        return new_node

    def append(self, data):
        new_node = Node(data, None, None)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node

        self.length += 1

        return new_node

    def remove_by_node(self, node):
        # if it's not the first element
        if node == self.head and node == self.tail:
            self.head = None
            self.tail = None
        elif node == self.head:
            self.head = node.next
            self.head.prev = None
        elif node == self.tail:
            self.tail = node.prev
            self.tail.next = None
        else:
            node.prev.next = node.next
            node.next.prev = node.prev

        self.length -= 1

        node.prev = None
        node.next = None
        return node

    def remove_by_value(self, node_value):
        current_node = self.head

        while current_node is not None:
            if current_node.data == node_value:
                return self.remove_by_node(current_node)

            current_node = current_node.next

        return None

    def remove_tail(self):
        return self.remove_by_node(self.tail)


class LRUCache(object):
    def __init__(self, size):
        self.size = size
        self.dll = DoubleList()
        self.hm = dict()

    def contains(self, key):
        return key in self.hm

    def all_entries(self):
        return self.hm.keys()

    def get_data(self, key):
        return self.hm[key]["data"] if key in self.hm else None

    def set_data(self, key, new_data):
        if key in self.hm:
            old_data = self.get_data(key)
            self.hm[key]["data"] = new_data
            return old_data

        return None

    def entry(self, key, data):
        old_key = None
        if self.contains(key):
            self.dll.remove_by_node(self.hm[key])
            del self.hm[key]
        elif self.dll.length == self.size:
            old_tail = self.dll.remove_tail()
            old_key = old_tail.data
            del self.hm[old_key]

        new_node = self.dll.prepend(key)
        self.hm[key] = {"node": new_node, "data": data}

        return old_key
