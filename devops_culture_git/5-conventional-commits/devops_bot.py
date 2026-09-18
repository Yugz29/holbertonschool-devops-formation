#!/usr/bin/env python3
"""A tiny DevOps maintenance bot."""


def bot_status(name, energy):
    energy = max(0, min(100, energy))
    return f"{name} is online with {energy}% energy"


def deploy():
    return "Deployment started"


if __name__ == "__main__":
    print(bot_status("HolbieBot", 100))
    print(deploy())
