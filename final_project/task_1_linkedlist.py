class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    # Додавання в кінець
    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        curr = self.head
        while curr.next:
            curr = curr.next
        curr.next = new_node

    # Вивід списку
    def print_list(self):
        curr = self.head
        while curr:
            print(curr.data, end=" -> ")
            curr = curr.next
        print("None")

    # Реверсування списку
    def reverse(self):
        prev = None
        curr = self.head
        while curr:
            nxt = curr.next
            curr.next = prev
            prev = curr
            curr = nxt
        self.head = prev

    # Сортування злиттям
    def merge_sort(self, head=None):
        if head is None:
            head = self.head
        if head is None or head.next is None:
            return head

        # пошук середини списку (slow/fast pointers)
        slow, fast = head, head.next
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next

        mid = slow.next
        slow.next = None

        left = self.merge_sort(head)
        right = self.merge_sort(mid)

        return self._merge_sorted(left, right)

    def sort(self):
        self.head = self.merge_sort(self.head)

    # Допоміжна функція для злиття
    def _merge_sorted(self, l1, l2):
        dummy = Node(0)
        tail = dummy
        while l1 and l2:
            if l1.data < l2.data:
                tail.next = l1
                l1 = l1.next
            else:
                tail.next = l2
                l2 = l2.next
            tail = tail.next
        tail.next = l1 or l2
        return dummy.next


# Функція злиття двох відсортованих списків
def merge_two_lists(l1, l2):
    dummy = Node(0)
    tail = dummy
    h1, h2 = l1.head, l2.head

    while h1 and h2:
        if h1.data < h2.data:
            tail.next = h1
            h1 = h1.next
        else:
            tail.next = h2
            h2 = h2.next
        tail = tail.next

    tail.next = h1 or h2
    merged = LinkedList()
    merged.head = dummy.next
    return merged


if __name__ == "__main__":
    # Створюємо список
    lst = LinkedList()
    for x in [4, 2, 1, 3]:
        lst.append(x)

    print("Оригінальний список:")
    lst.print_list()

    lst.reverse()
    print("Реверсований список:")
    lst.print_list()

    lst.sort()
    print("Відсортований список:")
    lst.print_list()

    # Другий список
    lst2 = LinkedList()
    for x in [0, 5, 6]:
        lst2.append(x)

    merged = merge_two_lists(lst, lst2)
    print("Об'єднаний відсортований список:")
    merged.print_list()