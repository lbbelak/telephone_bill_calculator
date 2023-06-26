import sys
import getopt
import pandas as pd
import numpy as np
from datetime import datetime, time
import unittest

expensive_hours = [8, 9, 10, 11, 12, 13, 14, 15]
expensive_start = time(8, 0, 0)
expensive_end = time(16, 0, 0)


class PhoneNumber:

    def __init__(self, phone_number) -> None:
        self.phone_number = phone_number
        self.calls = []
        self.total_minutes = 0
        self.total_price = 0

    def add_call(self, call):
        self.calls.append(call)
        self.total_minutes += call.total
        self.total_price += call.price


class Call:

    def __init__(self, phone_number, start, end) -> None:
        self.phone_number = phone_number
        self.start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        self.end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        self.total = np.ceil(
            ((self.end.timestamp() - self.start.timestamp()) - 1) / 60)
        self.price = self.calculate_price()
        if self.total > 5:
            self.price += 0.2 * (self.total - 5)

    def calculate_price(self):
        with_bonus = 0
        without_bonus = 0
        if self.start.hour in expensive_hours or self.end.hour in expensive_hours or (
                self.start.hour < expensive_start.hour
                and self.end.hour > expensive_end.hour):
            exp_start = datetime(self.start.year, self.start.month,
                                 self.start.day, expensive_start.hour,
                                 expensive_start.minute,
                                 expensive_start.second).timestamp()
            exp_end = datetime(self.start.year, self.start.month,
                               self.start.day, expensive_end.hour,
                               expensive_end.minute,
                               expensive_end.second).timestamp()
            if self.start.timestamp() < exp_start:
                without_bonus = (exp_start - self.start.timestamp())
                if self.end.timestamp() > exp_end:
                    with_bonus = exp_end - exp_start
                    without_bonus += self.end.timestamp() - exp_end
                else:
                    with_bonus = self.end.timestamp() - exp_start
            else:
                if self.end.timestamp() > exp_end:
                    with_bonus = exp_end - exp_start
                    without_bonus = self.end.timestamp() - exp_end
                else:
                    with_bonus = self.end.timestamp() - exp_start
        else:
            without_bonus = self.end.timestamp() - self.start.timestamp()
        return (np.ceil(with_bonus / 60)) + (np.ceil(without_bonus / 60)) / 2


def calculate(argv):
    inputfile = ''
    opts, _ = getopt.getopt(argv, "i:", ["ifile="])
    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            inputfile = arg
            read_database(inputfile=inputfile)


def read_database(inputfile: str):
    df = pd.read_csv(inputfile)
    cost = 0
    contacts = []
    for row in df.itertuples():
        call = Call(row._1, row._2, row._3)
        contact = find_contact(contacts, call.phone_number)
        if contact is None:
            contact = PhoneNumber(call.phone_number)
            contact.add_call(call)
            contacts.append(contact)
        else:
            contact.add_call(call)
    for contact in contacts:
        cost += contact.total_price
    cost += -find_favorite(contacts).total_price
    print("Calculated cost is ", np.ceil(cost))


def find_contact(contacts, phone_number):
    for contact in contacts:
        if contact.phone_number == phone_number:
            return contact
    return None


def find_favorite(contacts):
    contacts.sort(key=lambda x: x.total_minutes, reverse=True)
    winners = [contacts[0]]
    for contact in contacts:
        if contact.total_minutes == winners[0].total_minutes and sum_digits(
                contact.phone_number) > sum_digits(winners[0].phone_number):
            winners += contact
    return winners[0]


def sum_digits(n):
    return n % 10 + sum_digits(n // 10) if n > 9 else n


def test_find_favorite():
    contacts = []
    call_1 = Call(420600768405, "2022-05-21 10:50:13", "2022-05-21 10:52:11")
    call_2 = Call(420490506169, "2022-05-21 20:14:14", "2022-05-21 20:18:12")
    call_3 = Call(420448147315, "2022-05-24 04:32:01", "2022-05-24 04:35:14")
    call_4 = Call(420306421116, "2022-05-26 14:19:13", "2022-05-26 14:20:36")
    calls = [call_1, call_2, call_3, call_4]
    for call in calls:
        contact = find_contact(contacts, call.phone_number)
        if contact is None:
            contact = PhoneNumber(call.phone_number)
            contact.add_call(call)
            contacts.append(contact)
        else:
            contact.add_call(call)
    winner = find_favorite(contacts)
    assert winner.phone_number == 420490506169


if __name__ == "__main__":
    test_find_favorite()
    calculate(sys.argv[1:])
