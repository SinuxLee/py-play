# 链表（Linked List）
# 跳表（Skip List）
# LRU Cache（结合 Hash + 双向链表）


from dataclasses import dataclass, field
from typing import TypeVar, Union, Generic, List

T = TypeVar("T", bound=Union[int, float])


@dataclass(order=True)
class Node(Generic[T]):
    val: T
    next: "Node" = field(default=None, compare=False)
    prev: "Node" = field(default=None, compare=False)


class LinkedList(Generic[T]):
    def __init__(self):
        self.head = Node(None)  # 哨兵节点
        self.tail = Node(None)
        self.head.next = self.tail
        self.tail.prev = self.head

    def add_to_head(self, val: T) -> None:
        node = Node(val)
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def remove(self, node: Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def display(self) -> None:
        curr = self.head.next
        while curr != self.tail:
            print(curr.val, end=" -> ")
            curr = curr.next
        print("None")


ll: LinkedList[int] = LinkedList()
ll.add_to_head(1)
ll.add_to_head(2)
ll.add_to_head(3)
ll.display()
ll.remove(ll.head.next)  # 删除第一个节点
ll.display()
ll.remove(ll.tail.prev)  # 删除最后一个节点
ll.display()

print(ll.head)
